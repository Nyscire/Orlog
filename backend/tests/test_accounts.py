import re
import unittest

from accounts import Accounts
from db import Database
from errors import GameError


class Clock:
    def __init__(self):
        self.now = 1_700_000_000.0

    def __call__(self):
        return self.now


class FakeMailer:
    def __init__(self):
        self.sent = []

    def send(self, to, subject, body):
        self.sent.append((to, subject, body))

    def last_code(self):
        return re.search(r"\b(\d{6})\b", self.sent[-1][2]).group(1)


class AccountsTestCase(unittest.TestCase):
    def setUp(self):
        self.clock = Clock()
        self.mailer = FakeMailer()
        self.db = Database(":memory:")
        self.accounts = Accounts(self.db, self.mailer, clock=self.clock)

    def tearDown(self):
        self.db.close()

    def code(self, err):
        return err.exception.to_dict()["code"]

    def register(self, login="Astrid", email="astrid@example.com", password="tajne-haslo"):
        return self.accounts.register(login, email, password)


class TestRegister(AccountsTestCase):
    def test_register_creates_account_and_session(self):
        user, token = self.register(" Astrid ", " Astrid@Example.com ")
        self.assertEqual({k: user[k] for k in ("login", "email", "rating")},
                         {"login": "Astrid", "email": "Astrid@Example.com", "rating": 1000})
        self.assertTrue(token)
        self.assertEqual(self.accounts.session_user(token), user)

    def test_password_is_not_stored_in_plain_text(self):
        self.register(password="tajne-haslo")
        row = self.db.one("SELECT password_hash FROM users")
        self.assertNotIn("tajne-haslo", row["password_hash"])
        self.assertNotIn(self.register("Bjorn", "b@example.com")[1],
                         [r["token_hash"] for r in self.db.query("SELECT token_hash FROM sessions")])

    def test_login_and_email_are_unique_ignoring_case(self):
        self.register()
        with self.assertRaises(GameError) as err:
            self.register("ASTRID", "inny@example.com")
        self.assertEqual(self.code(err), "login_taken")
        with self.assertRaises(GameError) as err:
            self.register("Bjorn", "ASTRID@example.com")
        self.assertEqual(self.code(err), "email_taken")

    def test_invalid_data(self):
        for login, email, password, code in (
                ("ab", "a@example.com", "tajne-haslo", "login_invalid"),
                ("a" * 21, "a@example.com", "tajne-haslo", "login_invalid"),
                ("z spacją", "a@example.com", "tajne-haslo", "login_invalid"),
                (None, "a@example.com", "tajne-haslo", "login_invalid"),
                ("Astrid", "bez-malpy", "tajne-haslo", "email_invalid"),
                ("Astrid", "a@b", "tajne-haslo", "email_invalid"),
                ("Astrid", "a@example.com", "krotkie", "password_too_short"),
                ("Astrid", "a@example.com", "x" * 129, "password_too_long")):
            with self.assertRaises(GameError) as err:
                self.accounts.register(login, email, password)
            self.assertEqual(self.code(err), code, (login, email, password))
        self.assertEqual(self.db.one("SELECT COUNT(*) FROM users")[0], 0)

    def test_polish_letters_in_login(self):
        user, _ = self.register("Łukasz_Ż.1", "l@example.com")
        self.assertEqual(user["login"], "Łukasz_Ż.1")
        self.assertTrue(self.accounts.is_registered("łukasz_ż.1"))

    def test_registered_names(self):
        self.register()
        self.assertTrue(self.accounts.is_registered(" astrid "))
        self.assertFalse(self.accounts.is_registered("Bjorn"))


class TestLogin(AccountsTestCase):
    def test_login_with_login_or_email(self):
        self.register()
        for identifier in ("Astrid", "astrid", "ASTRID@example.com"):
            user, token = self.accounts.login(identifier, "tajne-haslo")
            self.assertEqual(user["login"], "Astrid")
            self.assertEqual(self.accounts.session_user(token)["login"], "Astrid")

    def test_wrong_password_or_unknown_account(self):
        self.register()
        for identifier, password in (("Astrid", "zle-haslo"), ("Nikt", "tajne-haslo"), ("", "x"), (None, None)):
            with self.assertRaises(GameError) as err:
                self.accounts.login(identifier, password)
            self.assertEqual(self.code(err), "bad_credentials")

    def test_too_many_failed_logins_block_the_account_for_a_while(self):
        self.register()
        for i in range(Accounts.LOGIN_FAILS):
            # login i e-mail liczą się razem
            with self.assertRaises(GameError):
                self.accounts.login("Astrid" if i % 2 else "astrid@example.com", "zle-haslo")
        with self.assertRaises(GameError) as err:
            self.accounts.login("Astrid", "tajne-haslo")
        self.assertEqual(err.exception.to_dict(), {"code": "too_many_attempts", "params": {"minutes": 15}})
        self.clock.now += Accounts.LOGIN_WINDOW
        self.assertEqual(self.accounts.login("Astrid", "tajne-haslo")[0]["login"], "Astrid")

    def test_logout_ends_only_that_session(self):
        _, first = self.register()
        _, second = self.accounts.login("Astrid", "tajne-haslo")
        self.accounts.logout(first)
        self.assertIsNone(self.accounts.session_user(first))
        self.assertIsNotNone(self.accounts.session_user(second))

    def test_unused_session_expires(self):
        _, token = self.register()
        self.clock.now += Accounts.SESSION_TTL - 1
        self.assertIsNotNone(self.accounts.session_user(token))   # używana sesja się przedłuża
        self.clock.now += Accounts.SESSION_TTL - 1
        self.assertIsNotNone(self.accounts.session_user(token))
        self.clock.now += Accounts.SESSION_TTL
        self.assertIsNone(self.accounts.session_user(token))
        for bad in (None, "", "zly-token", 5):
            self.assertIsNone(self.accounts.session_user(bad))


class TestPasswordReset(AccountsTestCase):
    def test_reset_with_code_from_email(self):
        _, old_token = self.register()
        self.accounts.request_reset("astrid", "pl")
        to, subject, body = self.mailer.sent[-1]
        self.assertEqual(to, "astrid@example.com")
        self.assertIn("Astrid", body)
        user, token = self.accounts.confirm_reset("Astrid", self.mailer.last_code(), "nowe-haslo-123")
        self.assertEqual(user["login"], "Astrid")
        self.assertIsNotNone(self.accounts.session_user(token))
        # stare hasło i stare sesje już nie działają
        self.assertIsNone(self.accounts.session_user(old_token))
        with self.assertRaises(GameError):
            self.accounts.login("Astrid", "tajne-haslo")
        self.assertEqual(self.accounts.login("Astrid", "nowe-haslo-123")[0]["login"], "Astrid")

    def test_mail_in_english(self):
        self.register()
        self.accounts.request_reset("astrid@example.com", "en")
        self.assertIn("password", self.mailer.sent[-1][1])

    def test_unknown_account_gets_no_mail_and_no_error(self):
        self.accounts.request_reset("Nikt", "pl")
        self.accounts.request_reset(None, "pl")
        self.assertEqual(self.mailer.sent, [])

    def test_code_is_single_use_and_expires(self):
        self.register()
        self.accounts.request_reset("Astrid")
        code = self.mailer.last_code()
        self.accounts.confirm_reset("Astrid", code, "nowe-haslo-123")
        with self.assertRaises(GameError) as err:
            self.accounts.confirm_reset("Astrid", code, "inne-haslo-123")
        self.assertEqual(self.code(err), "reset_code_invalid")
        self.accounts.request_reset("Astrid")
        self.clock.now += Accounts.RESET_TTL
        with self.assertRaises(GameError) as err:
            self.accounts.confirm_reset("Astrid", self.mailer.last_code(), "inne-haslo-123")
        self.assertEqual(self.code(err), "reset_code_invalid")

    def test_wrong_codes_burn_the_code(self):
        self.register()
        self.accounts.request_reset("Astrid")
        code = self.mailer.last_code()
        wrong = "000000" if code != "000000" else "111111"
        for _ in range(Accounts.RESET_ATTEMPTS):
            with self.assertRaises(GameError):
                self.accounts.confirm_reset("Astrid", wrong, "nowe-haslo-123")
        with self.assertRaises(GameError) as err:
            self.accounts.confirm_reset("Astrid", code, "nowe-haslo-123")
        self.assertEqual(self.code(err), "reset_code_invalid")

    def test_new_password_is_validated(self):
        self.register()
        self.accounts.request_reset("Astrid")
        with self.assertRaises(GameError) as err:
            self.accounts.confirm_reset("Astrid", self.mailer.last_code(), "krotkie")
        self.assertEqual(self.code(err), "password_too_short")

    def test_reset_requests_are_limited_quietly(self):
        self.register()
        with self.assertLogs("accounts", level="WARNING"):
            for _ in range(Accounts.RESET_REQUESTS + 2):
                self.accounts.request_reset("Astrid")
        self.assertEqual(len(self.mailer.sent), Accounts.RESET_REQUESTS)


if __name__ == "__main__":
    unittest.main()
