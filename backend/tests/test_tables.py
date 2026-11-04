import random
import unittest

from errors import GameError
from tables import TableManager


class Clock:
    def __init__(self):
        self.now = 1000.0

    def __call__(self):
        return self.now


class TablesTestCase(unittest.TestCase):
    def setUp(self):
        self.clock = Clock()
        self.tm = TableManager(rng=random.Random(1), clock=self.clock)

    def code(self, err):
        return err.exception.to_dict()["code"]

    def play_pair(self, a="Astrid", b="Bjorn", sids=("s1", "s2")):
        seat = self.tm.create_table(sids[0], a, ["Thor"])
        self.tm.join_table(sids[1], seat.table_id, b, ["Loki"])
        return self.tm.tables[seat.table_id]


class TestCreateAndJoin(TablesTestCase):
    def test_create_table_seats_host(self):
        seat = self.tm.create_table("s1", " Astrid ", ["Thor", "Freyja"], "Pod dębem")
        table = self.tm.tables[seat.table_id]
        self.assertEqual((seat.name, table.name, table.host, table.seats), ("Astrid", "Pod dębem", "Astrid", ["Astrid"]))
        self.assertEqual(table.stage, "waiting")
        self.assertEqual(len(seat.table_id), 4)
        self.assertTrue(seat.token)
        self.assertEqual(self.tm.table_of("s1"), (table, "Astrid"))

    def test_second_player_starts_the_game(self):
        table = self.play_pair()
        self.assertEqual(table.stage, "dice")
        self.assertEqual(list(table.game.players), ["Astrid", "Bjorn"])
        self.assertFalse(self.tm.is_open(table))

    def test_many_tables_play_independently(self):
        t1 = self.play_pair("A1", "B1", ("a1", "b1"))
        t2 = self.play_pair("A2", "B2", ("a2", "b2"))
        self.assertNotEqual(t1.id, t2.id)
        t1.game.confirm_dice("A1", [0, 1])
        self.assertEqual(t1.game.active_player, "B1")
        self.assertEqual(t2.game.active_player, "A2")
        self.assertEqual(len(t2.game.players["A2"].saved_dice), 0)

    def test_names_are_unique_across_tables(self):
        self.tm.create_table("s1", "Astrid")
        with self.assertRaises(GameError) as err:
            self.tm.create_table("s2", "Astrid")
        self.assertEqual(self.code(err), "name_taken")

    def test_one_seat_per_connection(self):
        seat = self.tm.create_table("s1", "Astrid")
        with self.assertRaises(GameError) as err:
            self.tm.create_table("s1", "Inna")
        self.assertEqual(err.exception.to_dict(), {"code": "already_seated", "params": {"name": "Astrid"}})
        with self.assertRaises(GameError):
            self.tm.join_table("s1", seat.table_id, "Inna")

    def test_join_errors(self):
        table = self.play_pair()
        with self.assertRaises(GameError) as err:
            self.tm.join_table("s3", table.id, "Cyra")
        self.assertEqual(self.code(err), "table_full")
        for bad in ("ZZZZ", None, 5):
            with self.assertRaises(GameError) as err:
                self.tm.join_table("s3", bad, "Cyra")
            self.assertEqual(self.code(err), "table_not_found")

    def test_invalid_input_leaves_no_table(self):
        for name, gods, table_name, code in (("", None, None, "name_required"),
                                             ("x" * 21, None, None, "name_too_long"),
                                             ("Astrid", ["Zeus"], None, "unknown_god"),
                                             ("Astrid", None, "x" * 31, "table_name_too_long"),
                                             ("Astrid", None, 7, "invalid_table_name")):
            with self.assertRaises(GameError) as err:
                self.tm.create_table("s1", name, gods, table_name)
            self.assertEqual(self.code(err), code)
        self.assertEqual((self.tm.tables, self.tm.seats, self.tm.sids), ({}, {}, {}))

    def test_table_limit(self):
        self.tm.MAX_TABLES = 2
        self.tm.create_table("s1", "A")
        self.tm.create_table("s2", "B")
        with self.assertRaises(GameError) as err:
            self.tm.create_table("s3", "C")
        self.assertEqual(self.code(err), "too_many_tables")
        self.assertTrue(self.tm.lobby_data()["full"])


class TestLeaving(TablesTestCase):
    def test_leaving_waiting_table_removes_it(self):
        seat = self.tm.create_table("s1", "Astrid")
        self.assertEqual(self.tm.leave("s1"), (None, "Astrid"))
        self.assertNotIn(seat.table_id, self.tm.tables)
        self.assertEqual((self.tm.seats, self.tm.sids), ({}, {}))
        self.assertIsNone(self.tm.leave("s1"))

    def test_opponent_stays_and_waits_after_leave(self):
        table = self.play_pair()
        table.game.confirm_dice("Astrid", [0])
        left = self.tm.leave("s1")
        self.assertEqual(left, (table, "Astrid"))
        self.assertEqual(table.stage, "waiting")
        self.assertEqual(table.seats, ["Bjorn"])
        self.assertEqual(table.host, "Bjorn")
        self.assertEqual([g.name for g in table.game.players["Bjorn"].gods], ["Loki"])
        self.assertEqual(table.notice, {"code": "player_left", "params": {"name": "Astrid"}})
        self.assertTrue(self.tm.is_open(table))
        # ktoś nowy się dosiada: nowa partia, informacja znika
        self.tm.join_table("s3", table.id, "Cyra")
        self.assertEqual(table.stage, "dice")
        self.assertIsNone(table.notice)
        self.assertEqual(self.tm.state(table)["notice"], None)

    def test_name_is_free_after_leaving(self):
        self.play_pair()
        self.tm.leave("s1")
        self.tm.create_table("s9", "Astrid")
        self.assertEqual(self.tm.seats["Astrid"].sid, "s9")

    def test_leave_after_finished_game(self):
        table = self.play_pair()
        table.game.players["Bjorn"].hp = 0
        table.game._check_winner()
        self.assertEqual(table.stage, "finished")
        self.tm.leave("s2")
        self.assertEqual((table.stage, table.seats), ("waiting", ["Astrid"]))


class TestConnections(TablesTestCase):
    def test_resume_with_token(self):
        table = self.play_pair()
        token = self.tm.seats["Astrid"].token
        self.assertIs(self.tm.disconnect("s1"), table)
        self.assertFalse(self.tm.is_connected("Astrid"))
        self.assertFalse(self.tm.state(table)["players"][0]["connected"])
        seat, previous = self.tm.resume("s1b", "Astrid", token)
        self.assertEqual((seat.sid, previous), ("s1b", None))
        self.assertTrue(self.tm.state(table)["players"][0]["connected"])

    def test_resume_needs_the_right_token(self):
        self.play_pair()
        self.tm.disconnect("s1")
        for name, token in (("Astrid", "zly"), ("Astrid", None), ("Nikt", "x"), (None, None)):
            with self.assertRaises(GameError) as err:
                self.tm.resume("s9", name, token)
            self.assertEqual(self.code(err), "seat_not_found")

    def test_resume_takes_over_another_tab(self):
        self.play_pair()
        token = self.tm.seats["Astrid"].token
        seat, previous = self.tm.resume("s1b", "Astrid", token)
        self.assertEqual(previous, "s1")
        self.assertIsNone(self.tm.seat_of("s1"))
        self.assertIsNone(self.tm.disconnect("s1"))   # stara karta nie wyrzuca gracza
        self.assertTrue(self.tm.is_connected("Astrid"))

    def test_waiting_table_with_offline_host_is_hidden_then_removed(self):
        seat = self.tm.create_table("s1", "Astrid")
        self.tm.disconnect("s1")
        self.assertEqual(self.tm.lobby_data()["tables"], [])
        with self.assertRaises(GameError):
            self.tm.join_table("s2", seat.table_id, "Bjorn")
        self.clock.now += TableManager.WAITING_GRACE - 1
        self.assertEqual(self.tm.sweep(), ([], False))
        self.assertIn(seat.table_id, self.tm.tables)
        self.clock.now += 2
        self.assertEqual(self.tm.sweep(), ([], True))
        self.assertNotIn(seat.table_id, self.tm.tables)
        self.assertNotIn("Astrid", self.tm.seats)

    def test_quick_return_keeps_the_waiting_table(self):
        seat = self.tm.create_table("s1", "Astrid")
        self.tm.disconnect("s1")
        self.clock.now += 5
        self.tm.resume("s1b", "Astrid", seat.token)
        self.clock.now += TableManager.WAITING_GRACE * 2
        self.tm.sweep()
        self.assertIn(seat.table_id, self.tm.tables)

    def test_game_keeps_seat_of_offline_player(self):
        table = self.play_pair()
        self.tm.disconnect("s2")
        self.clock.now += TableManager.ABANDONED_GRACE * 2
        self.assertEqual(self.tm.sweep(), ([], False))
        self.assertEqual(table.seats, ["Astrid", "Bjorn"])

    def test_abandoned_game_is_removed(self):
        table = self.play_pair()
        self.tm.disconnect("s1")
        self.clock.now += 100
        self.tm.disconnect("s2")
        self.clock.now += TableManager.ABANDONED_GRACE - 50
        self.tm.sweep()
        self.assertIn(table.id, self.tm.tables)   # drugi gracz rozłączył się niedawno
        self.clock.now += 60
        self.assertEqual(self.tm.sweep(), ([], True))
        self.assertEqual((self.tm.tables, self.tm.seats), ({}, {}))


class TestLobbyData(TablesTestCase):
    def test_open_tables_first(self):
        self.clock.now = 1
        busy = self.play_pair("A1", "B1", ("a1", "b1"))
        self.clock.now = 2
        free = self.tm.create_table("c1", "C1", None, "Szybka partia")
        data = self.tm.lobby_data()
        self.assertEqual([t["id"] for t in data["tables"]], [free.table_id, busy.id])
        self.assertEqual(data["tables"][0], {"id": free.table_id, "name": "Szybka partia", "host": "C1",
                                             "players": ["C1"], "ratings": {}, "stage": "waiting", "round": 1,
                                             "ranked": False, "open": True})
        self.assertEqual(data["tables"][1]["players"], ["A1", "B1"])
        self.assertFalse(data["tables"][1]["open"])
        self.assertEqual(len(data["gods"]), 20)
        self.assertEqual(data["max_gods"], 3)

    def test_state_carries_table_info(self):
        table = self.play_pair()
        state = self.tm.state(table)
        self.assertEqual(state["table"], {"id": table.id, "name": None, "host": "Astrid",
                                          "ranked": False, "forfeit_grace": None})
        self.assertEqual(state["stage"], "dice")
        self.assertTrue(all(p["connected"] for p in state["players"]))
        self.assertEqual([(p["account"], p["rating"]) for p in state["players"]], [(False, None), (False, None)])
        self.assertIsNone(state["result"])


class RankedTestCase(unittest.TestCase):
    """Stoły rankingowe, konta przy stole i zapis wyników (zamiast bazy: lista wyników)."""

    def setUp(self):
        self.clock = Clock()
        self.results = []
        self.registered = {"astrid", "bjorn", "cyra"}

        def recorder(result):
            self.results.append(result)
            if not result["ranked"]:
                return {}
            return {p["name"]: {"before": 1000, "after": 1016 if p["won"] else 984} for p in result["players"]}

        self.tm = TableManager(rng=random.Random(1), clock=self.clock,
                               reserved=lambda name: name.casefold() in self.registered, recorder=recorder)
        self.users = {name: {"id": i + 1, "login": name, "rating": 1000}
                      for i, name in enumerate(("Astrid", "Bjorn", "Cyra"))}

    def code(self, err):
        return err.exception.to_dict()["code"]

    def ranked_pair(self, a="Astrid", b="Bjorn"):
        seat = self.tm.create_table("s1", None, ["Thor"], None, True, self.users[a])
        self.tm.join_table("s2", seat.table_id, None, ["Loki"], self.users[b])
        return self.tm.tables[seat.table_id]

    def finish(self, table, loser):
        table.game.players[loser].hp = 0
        table.game._check_winner()
        self.tm.after_action(table)


class TestRankedSeats(RankedTestCase):
    def test_ranked_tables_need_an_account(self):
        with self.assertRaises(GameError) as err:
            self.tm.create_table("s1", "Gość", None, None, True)
        self.assertEqual(self.code(err), "ranked_login_required")
        seat = self.tm.create_table("s1", None, None, None, True, self.users["Astrid"])
        with self.assertRaises(GameError) as err:
            self.tm.join_table("s2", seat.table_id, "Gość")
        self.assertEqual(self.code(err), "ranked_login_required")
        self.assertTrue(self.tm.lobby_data()["tables"][0]["ranked"])

    def test_account_plays_under_its_login(self):
        seat = self.tm.create_table("s1", "Inne imię", None, None, False, self.users["Astrid"])
        self.assertEqual(seat.name, "Astrid")
        self.assertEqual((seat.user_id, seat.rating), (1, 1000))
        with self.assertRaises(GameError) as err:
            self.tm.create_table("s2", None, None, None, False, self.users["Astrid"])
        self.assertEqual(self.code(err), "account_busy")

    def test_guests_cannot_use_registered_names(self):
        with self.assertRaises(GameError) as err:
            self.tm.create_table("s1", " ASTRID ")
        self.assertEqual(self.code(err), "name_reserved")
        self.assertEqual(self.tm.create_table("s1", "Gunnar").name, "Gunnar")

    def test_guest_and_account_can_play_normal_games(self):
        seat = self.tm.create_table("s1", "Gunnar")
        self.tm.join_table("s2", seat.table_id, None, None, self.users["Astrid"])
        table = self.tm.tables[seat.table_id]
        self.assertEqual(table.stage, "dice")
        state = self.tm.state(table)
        self.assertEqual({p["name"]: (p["account"], p["rating"]) for p in state["players"]},
                         {"Gunnar": (False, None), "Astrid": (True, None)})
        self.assertEqual(self.tm.lobby_data()["tables"][0]["ratings"], {"Astrid": 1000})


class TestResults(RankedTestCase):
    def test_finished_game_is_recorded_once(self):
        table = self.ranked_pair()
        self.finish(table, "Bjorn")
        self.tm.after_action(table)
        self.assertEqual(len(self.results), 1)
        result = self.results[0]
        self.assertEqual((result["ranked"], result["forfeit"]), (True, False))
        self.assertEqual([(p["name"], p["user_id"], p["won"], p["gods"]) for p in result["players"]],
                         [("Astrid", 1, True, ["Thor"]), ("Bjorn", 2, False, ["Loki"])])
        state = self.tm.state(table)
        self.assertEqual(state["result"]["Astrid"], {"before": 1000, "after": 1016})
        self.assertEqual({p["name"]: p["rating"] for p in state["players"]}, {"Astrid": 1016, "Bjorn": 984})
        self.assertEqual(self.tm.pop_rating_changes(), {"Astrid": 1016, "Bjorn": 984})
        self.assertEqual(self.tm.pop_rating_changes(), {})

    def test_rematch_is_recorded_again(self):
        table = self.ranked_pair()
        self.finish(table, "Bjorn")
        table.game.rematch()
        self.tm.after_action(table)
        self.assertIsNone(self.tm.state(table)["result"])
        self.finish(table, "Astrid")
        self.assertEqual(len(self.results), 2)

    def test_leaving_a_ranked_game_is_a_forfeit(self):
        table = self.ranked_pair()
        self.tm.leave("s2")
        self.assertEqual(len(self.results), 1)
        self.assertTrue(self.results[0]["forfeit"])
        self.assertEqual([(p["name"], p["won"]) for p in self.results[0]["players"]],
                         [("Astrid", True), ("Bjorn", False)])
        # zwycięzca czeka przy stole na nowego rywala
        self.assertEqual(table.stage, "waiting")
        self.assertEqual(table.notice, {"code": "opponent_forfeit", "params": {"name": "Bjorn"}})
        self.assertEqual(self.tm.pop_rating_changes(), {"Astrid": 1016, "Bjorn": 984})

    def test_leaving_a_normal_game_records_nothing(self):
        seat = self.tm.create_table("s1", None, None, None, False, self.users["Astrid"])
        self.tm.join_table("s2", seat.table_id, None, None, self.users["Bjorn"])
        self.tm.leave("s2")
        self.assertEqual(self.results, [])
        self.assertEqual(self.tm.tables[seat.table_id].notice["code"], "player_left")

    def test_leaving_after_the_end_records_nothing_more(self):
        table = self.ranked_pair()
        self.finish(table, "Bjorn")
        self.tm.leave("s2")
        self.assertEqual(len(self.results), 1)

    def test_offline_player_loses_ranked_game_after_grace(self):
        table = self.ranked_pair()
        self.tm.disconnect("s2")
        self.clock.now += TableManager.RANKED_FORFEIT_GRACE - 1
        self.assertEqual(self.tm.sweep(), ([], False))
        self.clock.now += 1
        changed, list_changed = self.tm.sweep()
        self.assertEqual((changed, list_changed), ([table], True))
        self.assertEqual(table.stage, "finished")
        self.assertEqual(table.game.winner.name, "Astrid")
        self.assertTrue(self.results[0]["forfeit"])
        self.assertEqual(table.game.log[-1]["type"], "forfeit")
        # wraca już po wszystkim i widzi wynik
        self.tm.resume("s3", "Bjorn", self.tm.seats["Bjorn"].token)
        self.assertEqual(self.tm.sweep(), ([], False))
        self.assertEqual(len(self.results), 1)

    def test_normal_games_have_no_forfeit_timer(self):
        seat = self.tm.create_table("s1", None, None, None, False, self.users["Astrid"])
        self.tm.join_table("s2", seat.table_id, None, None, self.users["Bjorn"])
        self.tm.disconnect("s2")
        self.clock.now += TableManager.RANKED_FORFEIT_GRACE * 2
        self.tm.sweep()
        self.assertEqual(self.tm.tables[seat.table_id].stage, "dice")
        self.assertEqual(self.results, [])

    def test_both_offline_ranked_game_is_just_removed(self):
        table = self.ranked_pair()
        self.tm.disconnect("s1")
        self.tm.disconnect("s2")
        self.clock.now += TableManager.ABANDONED_GRACE
        self.tm.sweep()
        self.assertNotIn(table.id, self.tm.tables)
        self.assertEqual(self.results, [])

    def test_storage_error_does_not_stop_the_game(self):
        def broken(result):
            raise RuntimeError("baza padła")
        self.tm.recorder = broken
        table = self.ranked_pair()
        with self.assertLogs("tables", level="ERROR"):
            self.finish(table, "Bjorn")
        self.assertEqual(table.stage, "finished")
        self.assertIsNone(self.tm.state(table)["result"])
        table.game.rematch()
        self.tm.after_action(table)
        self.assertEqual(table.stage, "dice")


if __name__ == "__main__":
    unittest.main()
