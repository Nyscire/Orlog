import unittest

from accounts import Accounts
from db import Database
from stats import Stats, elo_change


class Clock:
    def __init__(self):
        self.now = 1_700_000_000.0

    def __call__(self):
        self.now += 1
        return self.now


class NoMail:
    def send(self, *args):
        pass


def player(name, user_id=None, won=False, hp=0, gods=("Thor",)):
    return {"name": name, "user_id": user_id, "won": won, "hp": hp, "gods": list(gods)}


class StatsTestCase(unittest.TestCase):
    def setUp(self):
        self.db = Database(":memory:")
        clock = Clock()
        self.accounts = Accounts(self.db, NoMail(), clock=clock)
        self.stats = Stats(self.db, clock=clock)
        self.ids = {}
        for login in ("Astrid", "Bjorn", "Cyra"):
            user, _ = self.accounts.register(login, f"{login.lower()}@example.com", "tajne-haslo")
            self.ids[login] = user["id"]

    def tearDown(self):
        self.db.close()

    def ranked(self, winner, loser, **extra):
        return self.stats.record_match({"ranked": True, "rounds": 5, "forfeit": extra.get("forfeit", False), "players": [
            player(winner, self.ids[winner], True, 7, extra.get("winner_gods", ("Thor",))),
            player(loser, self.ids[loser], False, 0, extra.get("loser_gods", ("Loki",)))]})


class TestElo(unittest.TestCase):
    def test_equal_ratings(self):
        self.assertEqual(elo_change(1000, 1000, 32), 16)

    def test_favourite_wins_less(self):
        self.assertLess(elo_change(1400, 1000, 32), 16)
        self.assertGreater(elo_change(1000, 1400, 32), 16)
        self.assertGreaterEqual(elo_change(3000, 0, 32), 1)


class TestRecord(StatsTestCase):
    def test_ranked_game_changes_ratings(self):
        changes = self.ranked("Astrid", "Bjorn")
        self.assertEqual(changes, {"Astrid": {"before": 1000, "after": 1016}, "Bjorn": {"before": 1000, "after": 984}})
        self.assertEqual(self.accounts.user(self.ids["Astrid"])["rating"], 1016)
        self.assertEqual(self.accounts.user(self.ids["Bjorn"])["rating"], 984)
        # po wygranej faworyta zmiana jest mniejsza
        self.assertLess(self.ranked("Astrid", "Bjorn")["Astrid"]["after"] - 1016, 16)

    def test_normal_game_is_recorded_without_rating(self):
        changes = self.stats.record_match({"ranked": False, "rounds": 3, "forfeit": False, "players": [
            player("Astrid", self.ids["Astrid"], True, 4), player("Gość", None, False, 0)]})
        self.assertEqual(changes, {})
        self.assertEqual(self.accounts.user(self.ids["Astrid"])["rating"], 1000)
        profile = self.stats.profile("Astrid")
        self.assertEqual(profile["totals"]["normal"], {"games": 1, "wins": 1, "losses": 0})
        self.assertEqual(profile["totals"]["ranked"], {"games": 0, "wins": 0, "losses": 0})
        match = profile["history"]["matches"][0]
        self.assertEqual(match["opponent"], {"name": "Gość", "account": False, "hp": 0, "gods": ["Thor"]})
        self.assertIsNone(match["rating"])
        self.assertIsNone(profile["position"])

    def test_ranked_needs_two_accounts(self):
        changes = self.stats.record_match({"ranked": True, "rounds": 3, "forfeit": False, "players": [
            player("Astrid", self.ids["Astrid"], True), player("Gość", None, False)]})
        self.assertEqual(changes, {})
        self.assertEqual(self.db.one("SELECT ranked FROM matches")[0], 0)

    def test_guest_only_games_are_not_stored(self):
        self.stats.record_match({"ranked": False, "rounds": 3, "forfeit": False,
                                 "players": [player("G1", None, True), player("G2", None, False)]})
        self.assertEqual(self.db.one("SELECT COUNT(*) FROM matches")[0], 0)


class TestProfile(StatsTestCase):
    def test_totals_history_and_gods(self):
        self.ranked("Astrid", "Bjorn", winner_gods=("Thor", "Freyja"), loser_gods=("Loki",))
        self.ranked("Bjorn", "Astrid", winner_gods=("Loki",), loser_gods=("Thor", "Idun"), forfeit=True)
        self.ranked("Astrid", "Cyra", winner_gods=("Thor",))
        profile = self.stats.profile("astrid")
        self.assertEqual(profile["login"], "Astrid")
        self.assertEqual(profile["totals"]["all"], {"games": 3, "wins": 2, "losses": 1})
        self.assertEqual(profile["totals"]["ranked"], {"games": 3, "wins": 2, "losses": 1})
        self.assertEqual(profile["gods"][0], {"name": "Thor", "games": 3, "wins": 2})
        self.assertEqual({g["name"] for g in profile["gods"]}, {"Thor", "Freyja", "Idun"})
        history = profile["history"]["matches"]
        self.assertEqual([m["opponent"]["name"] for m in history], ["Cyra", "Bjorn", "Bjorn"])
        self.assertEqual([m["won"] for m in history], [True, False, True])
        self.assertTrue(history[1]["forfeit"])
        self.assertEqual(history[2]["rating"], {"before": 1000, "after": 1016})
        self.assertEqual(profile["peak"], max(m["rating"]["after"] for m in history))
        self.assertIsNone(self.stats.profile("Nikt"))

    def test_history_pages(self):
        for _ in range(Stats.HISTORY_PAGE + 5):
            self.ranked("Astrid", "Bjorn")
        first = self.stats.history_of("Astrid")
        self.assertEqual(len(first["matches"]), Stats.HISTORY_PAGE)
        self.assertTrue(first["more"])
        rest = self.stats.history_of("Astrid", first["matches"][-1]["id"])
        self.assertEqual(len(rest["matches"]), 5)
        self.assertFalse(rest["more"])
        self.assertEqual(rest["login"], "Astrid")


class TestRanking(StatsTestCase):
    def test_ranking_order_and_positions(self):
        self.ranked("Astrid", "Bjorn")
        self.ranked("Astrid", "Bjorn")
        ranking = self.stats.ranking()
        self.assertEqual([p["login"] for p in ranking], ["Astrid", "Bjorn"])
        self.assertEqual(ranking[0]["position"], 1)
        self.assertEqual((ranking[0]["wins"], ranking[0]["losses"]), (2, 0))
        # Cyra nie grała rankingowo, więc nie ma jej w rankingu
        self.assertNotIn("Cyra", [p["login"] for p in ranking])
        self.assertEqual(self.stats.profile("Bjorn")["position"], 2)
        self.assertIsNone(self.stats.profile("Cyra")["position"])

    def test_equal_ratings_share_a_position(self):
        self.ranked("Astrid", "Bjorn")
        self.ranked("Bjorn", "Astrid")    # obaj znów blisko 1000, ale nie równo
        self.db.conn.execute("UPDATE users SET rating = 1000")
        self.assertEqual([p["position"] for p in self.stats.ranking()], [1, 1])
        self.assertEqual(self.stats.profile("Bjorn")["position"], 1)


if __name__ == "__main__":
    unittest.main()
