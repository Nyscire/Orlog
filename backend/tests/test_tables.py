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
                                             "players": ["C1"], "stage": "waiting", "round": 1, "open": True})
        self.assertEqual(data["tables"][1]["players"], ["A1", "B1"])
        self.assertFalse(data["tables"][1]["open"])
        self.assertEqual(len(data["gods"]), 20)
        self.assertEqual(data["max_gods"], 3)

    def test_state_carries_table_info(self):
        table = self.play_pair()
        state = self.tm.state(table)
        self.assertEqual(state["table"], {"id": table.id, "name": None, "host": "Astrid"})
        self.assertEqual(state["stage"], "dice")
        self.assertTrue(all(p["connected"] for p in state["players"]))


if __name__ == "__main__":
    unittest.main()
