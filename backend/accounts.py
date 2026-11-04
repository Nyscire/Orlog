"""Konta graczy: rejestracja, logowanie, sesje i reset hasła kodem z maila.

Hasła trzymamy jako skrót scrypt (werkzeug), a sesje jako skrót tokenu, więc
z samej bazy nie da się zalogować na cudze konto. Błędy idą jako GameError
z kodem, a tekst w języku gracza robi frontend (errors.<kod>).
"""
from __future__ import annotations

import hashlib
import hmac
import logging
import re
import secrets
import time
from collections import defaultdict, deque
from typing import Callable, Deque, Dict, Optional, Tuple

from werkzeug.security import check_password_hash, generate_password_hash

from db import Database
from errors import GameError
from mailer import Mailer

log = logging.getLogger(__name__)

LOGIN_RE = re.compile(r"^[\w.-]+$")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

RESET_MAIL = {
    "pl": ("Orlog: kod do zmiany hasła",
           "Cześć {login}!\n\n"
           "Twój kod do ustawienia nowego hasła w Orlogu: {code}\n"
           "Kod jest ważny przez {minutes} minut.\n\n"
           "Jeśli to nie Ty prosiłeś o zmianę hasła, po prostu zignoruj tę wiadomość."),
    "en": ("Orlog: password reset code",
           "Hi {login}!\n\n"
           "Your code for setting a new Orlog password: {code}\n"
           "The code is valid for {minutes} minutes.\n\n"
           "If you didn't ask for a new password, just ignore this message."),
}


def hash_secret(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


class Limiter:
    """Ile razy coś może się zdarzyć w oknie czasu (np. nieudane logowania na jedno konto)."""

    def __init__(self, limit: int, window: float, clock: Callable[[], float]) -> None:
        self.limit = limit
        self.window = window
        self.clock = clock
        self.events: Dict[str, Deque[float]] = defaultdict(deque)

    def _trim(self, key: str) -> Deque[float]:
        events = self.events[key]
        now = self.clock()
        while events and now - events[0] >= self.window:
            events.popleft()
        if not events:
            self.events.pop(key, None)
        return events

    def blocked(self, key: str) -> bool:
        return len(self._trim(key)) >= self.limit

    def hit(self, key: str) -> None:
        self._trim(key)
        self.events[key].append(self.clock())

    def clear(self, key: str) -> None:
        self.events.pop(key, None)


class Accounts:
    LOGIN_MIN, LOGIN_MAX = 3, 20          # tyle, ile może mieć imię przy stole
    PASSWORD_MIN, PASSWORD_MAX = 8, 128
    EMAIL_MAX = 254
    START_RATING = 1000
    SESSION_TTL = 180 * 24 * 3600         # s bez używania, po których sesja wygasa
    RESET_TTL = 15 * 60
    RESET_ATTEMPTS = 5                    # błędnych kodów, po których kod przepada
    LOGIN_FAILS, LOGIN_WINDOW = 10, 15 * 60
    RESET_REQUESTS, RESET_WINDOW = 3, 60 * 60

    def __init__(self, db: Database, mailer: Optional[Mailer] = None,
                 clock: Callable[[], float] = time.time) -> None:
        self.db = db
        self.mailer = mailer or Mailer()
        self.clock = clock
        self.failed_logins = Limiter(self.LOGIN_FAILS, self.LOGIN_WINDOW, clock)
        self.reset_requests = Limiter(self.RESET_REQUESTS, self.RESET_WINDOW, clock)
        # porównanie z tym skrótem, gdy konta nie ma: odpowiedź trwa tyle samo co przy złym haśle
        self._dummy_hash = generate_password_hash(secrets.token_hex(8))

    # ---------- dane ----------

    @staticmethod
    def public(row) -> Optional[Dict[str, object]]:
        """Konto tak, jak widzi je sam właściciel."""
        if row is None:
            return None
        return {"id": row["id"], "login": row["login"], "email": row["email"], "rating": row["rating"]}

    def user(self, user_id: int) -> Optional[Dict[str, object]]:
        return self.public(self.db.one("SELECT * FROM users WHERE id = ?", (user_id,)))

    def _find(self, identifier) -> Optional[object]:
        """Konto po loginie albo adresie e-mail."""
        if not isinstance(identifier, str) or not identifier.strip():
            return None
        identifier = identifier.strip()
        if "@" in identifier:
            return self.db.one("SELECT * FROM users WHERE email_key = ?", (identifier.lower(),))
        return self.db.one("SELECT * FROM users WHERE login_key = ?", (identifier.casefold(),))

    def is_registered(self, name: str) -> bool:
        """Czy imię należy do konta (gość nie może grać pod cudzym loginem)."""
        return self.db.one("SELECT 1 FROM users WHERE login_key = ?", (name.strip().casefold(),)) is not None

    # ---------- sprawdzanie danych ----------

    def _check_login(self, login) -> str:
        if not isinstance(login, str):
            raise GameError("login_invalid", min=self.LOGIN_MIN, max=self.LOGIN_MAX)
        login = login.strip()
        if not (self.LOGIN_MIN <= len(login) <= self.LOGIN_MAX) or not LOGIN_RE.match(login):
            raise GameError("login_invalid", min=self.LOGIN_MIN, max=self.LOGIN_MAX)
        return login

    def _check_email(self, email) -> str:
        if not isinstance(email, str) or len(email.strip()) > self.EMAIL_MAX or not EMAIL_RE.match(email.strip()):
            raise GameError("email_invalid")
        return email.strip()

    def _check_password(self, password) -> str:
        if not isinstance(password, str) or len(password) < self.PASSWORD_MIN:
            raise GameError("password_too_short", min=self.PASSWORD_MIN)
        if len(password) > self.PASSWORD_MAX:
            raise GameError("password_too_long", max=self.PASSWORD_MAX)
        return password

    # ---------- sesje ----------

    def _new_session(self, conn, user_id: int) -> str:
        token = secrets.token_urlsafe(32)
        now = self.clock()
        conn.execute("INSERT INTO sessions (token_hash, user_id, created_at, last_used) VALUES (?, ?, ?, ?)",
                     (hash_secret(token), user_id, now, now))
        # przy okazji sprzątamy stare sesje tego konta
        conn.execute("DELETE FROM sessions WHERE user_id = ? AND last_used < ?", (user_id, now - self.SESSION_TTL))
        return token

    def session_user(self, token) -> Optional[Dict[str, object]]:
        """Konto zalogowane tym tokenem (aplikacja wysyła go przy każdym połączeniu)."""
        if not isinstance(token, str) or not token:
            return None
        now = self.clock()
        with self.db.transaction() as conn:
            row = conn.execute(
                "SELECT users.*, sessions.last_used FROM sessions JOIN users ON users.id = sessions.user_id "
                "WHERE sessions.token_hash = ?", (hash_secret(token),)).fetchone()
            if row is None:
                return None
            if now - row["last_used"] >= self.SESSION_TTL:
                conn.execute("DELETE FROM sessions WHERE token_hash = ?", (hash_secret(token),))
                return None
            conn.execute("UPDATE sessions SET last_used = ? WHERE token_hash = ?", (now, hash_secret(token)))
        return self.public(row)

    def logout(self, token) -> None:
        if isinstance(token, str) and token:
            with self.db.transaction() as conn:
                conn.execute("DELETE FROM sessions WHERE token_hash = ?", (hash_secret(token),))

    # ---------- rejestracja i logowanie ----------

    def register(self, login, email, password) -> Tuple[Dict[str, object], str]:
        login = self._check_login(login)
        email = self._check_email(email)
        password = self._check_password(password)
        password_hash = generate_password_hash(password)
        with self.db.transaction() as conn:
            if conn.execute("SELECT 1 FROM users WHERE login_key = ?", (login.casefold(),)).fetchone():
                raise GameError("login_taken")
            if conn.execute("SELECT 1 FROM users WHERE email_key = ?", (email.lower(),)).fetchone():
                raise GameError("email_taken")
            cursor = conn.execute(
                "INSERT INTO users (login, login_key, email, email_key, password_hash, rating, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (login, login.casefold(), email, email.lower(), password_hash, self.START_RATING, self.clock()))
            user_id = cursor.lastrowid
            token = self._new_session(conn, user_id)
        return self.user(user_id), token

    def login(self, identifier, password) -> Tuple[Dict[str, object], str]:
        if not isinstance(identifier, str) or not identifier.strip() or not isinstance(password, str):
            raise GameError("bad_credentials")
        row = self._find(identifier)
        # limit liczymy na konto, niezależnie od tego, czy ktoś wpisuje login, czy e-mail
        key = row["login_key"] if row is not None else identifier.strip().casefold()
        if self.failed_logins.blocked(key):
            raise GameError("too_many_attempts", minutes=self.LOGIN_WINDOW // 60)
        if row is None or not check_password_hash(row["password_hash"], password):
            if row is None:
                check_password_hash(self._dummy_hash, password)
            self.failed_logins.hit(key)
            raise GameError("bad_credentials")
        self.failed_logins.clear(key)
        with self.db.transaction() as conn:
            token = self._new_session(conn, row["id"])
        return self.public(row), token

    # ---------- reset hasła ----------

    def request_reset(self, identifier, lang: str = "pl") -> None:
        """Wysyła kod na adres konta. Nie zdradza, czy takie konto istnieje."""
        row = self._find(identifier)
        if row is None:
            return
        if self.reset_requests.blocked(str(row["id"])):
            # bez błędu dla gracza, żeby nie zdradzać, że konto istnieje
            log.warning("Za dużo próśb o reset hasła dla %s", row["login"])
            return
        self.reset_requests.hit(str(row["id"]))
        code = f"{secrets.randbelow(10 ** 6):06d}"
        with self.db.transaction() as conn:
            conn.execute("INSERT OR REPLACE INTO reset_codes (user_id, code_hash, expires_at, attempts) "
                         "VALUES (?, ?, ?, 0)", (row["id"], hash_secret(f"{row['id']}:{code}"), self.clock() + self.RESET_TTL))
        subject, body = RESET_MAIL.get(lang, RESET_MAIL["pl"])
        self.mailer.send(row["email"], subject,
                         body.format(login=row["login"], code=code, minutes=self.RESET_TTL // 60))

    def confirm_reset(self, identifier, code, password) -> Tuple[Dict[str, object], str]:
        """Nowe hasło po podaniu kodu z maila. Wylogowuje wszystkie stare sesje."""
        password = self._check_password(password)
        row = self._find(identifier)
        code = code.strip().replace(" ", "") if isinstance(code, str) else ""
        with self.db.transaction() as conn:
            saved = conn.execute("SELECT * FROM reset_codes WHERE user_id = ?",
                                 (row["id"],)).fetchone() if row else None
            if saved is None or saved["expires_at"] <= self.clock() or saved["attempts"] >= self.RESET_ATTEMPTS:
                raise GameError("reset_code_invalid")
            if not hmac.compare_digest(saved["code_hash"], hash_secret(f"{row['id']}:{code}")):
                conn.execute("UPDATE reset_codes SET attempts = attempts + 1 WHERE user_id = ?", (row["id"],))
                # błędna próba musi zostać zapisana mimo błędu, więc wychodzimy bez wyjątku z transakcji
                wrong = True
            else:
                wrong = False
                conn.execute("UPDATE users SET password_hash = ? WHERE id = ?",
                             (generate_password_hash(password), row["id"]))
                conn.execute("DELETE FROM reset_codes WHERE user_id = ?", (row["id"],))
                conn.execute("DELETE FROM sessions WHERE user_id = ?", (row["id"],))
                token = self._new_session(conn, row["id"])
        if wrong:
            raise GameError("reset_code_invalid")
        self.failed_logins.clear(row["login_key"])
        return self.user(row["id"]), token
