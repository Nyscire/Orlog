import unittest

from die import Die
from game import Game, GameError
from god import god_factory


def dice(*faces):
    """Kości z listy nazw; sufiks '+' oznacza kość dającą manę, np. 'axe+'."""
    return [Die(face.rstrip('+'), face.endswith('+')) for face in faces]


NEUTRAL = ('shield',) * 6


class GameTestCase(unittest.TestCase):
    def setUp(self):
        self.game = Game()
        self.a = self.game.register_player("A")
        self.b = self.game.register_player("B")
        self.game.start()

    def keep_all(self, player, faces):
        """Aktywny gracz dostaje podane kości i zachowuje wszystkie."""
        self.assertEqual(self.game.active_player, player.name)
        player.rolled_dice = dice(*faces)
        self.game.confirm_dice(player.name, list(range(len(faces))))

    def dice_phase(self, a_faces=NEUTRAL, b_faces=NEUTRAL):
        leader = self.game.players[self.game.leader]
        other = self.game.opponent_of(leader)
        faces = {self.a.name: a_faces, self.b.name: b_faces}
        self.keep_all(leader, faces[leader.name])
        self.keep_all(other, faces[other.name])
        self.assertEqual(self.game.stage, "gods")

    def gods_phase(self, a_choice=(None, None), b_choice=(None, None)):
        choices = {self.a.name: a_choice, self.b.name: b_choice}
        first = self.game.leader
        second = self.game.opponent_of(self.game.players[first]).name
        self.game.choose_god(first, *choices[first])
        self.game.choose_god(second, *choices[second])


class TestGods(GameTestCase):
    def test_mana_costs_are_integers(self):
        costs = {god.name: god.mana_costs for god in god_factory()}
        self.assertEqual(costs["Thor"], [3, 4, 5])

    def test_god_costs_mana(self):
        self.a.mana = 2
        self.dice_phase()
        self.gods_phase(a_choice=("Freya", 1))
        self.assertEqual(self.a.mana, 0)
        self.assertEqual(self.a.hp, 23)

    def test_cannot_choose_unaffordable_god(self):
        self.dice_phase()
        with self.assertRaises(GameError):
            self.game.choose_god("A", "Thor", 1)
        self.assertEqual(self.game.active_player, "A")
        self.assertIsNone(self.a.chosen_god)

    def test_mana_from_saved_dice_counts_towards_cost(self):
        self.dice_phase(a_faces=('mana+', 'mana', 'shield', 'shield', 'shield', 'shield'))
        self.assertEqual(self.a.mana_available, 3)
        self.gods_phase(a_choice=("Thor", 1))
        self.assertEqual(self.b.hp, 18)
        self.assertEqual(self.a.mana, 0)

    def test_player_can_skip_god(self):
        self.dice_phase()
        self.gods_phase()
        self.assertEqual(self.game.round, 2)

    def test_invalid_level_is_rejected(self):
        self.a.mana = 10
        self.dice_phase()
        for level in (0, 4, "2", True, 1.0, None):
            with self.assertRaises(GameError, msg=repr(level)):
                self.game.choose_god("A", "Thor", level)

    def test_unknown_god_is_rejected(self):
        self.dice_phase()
        with self.assertRaises(GameError):
            self.game.choose_god("A", "Zeus", 1)

    def test_heimdall_boosts_own_axes_for_one_round(self):
        self.a.mana = 5
        self.dice_phase(a_faces=('axe',) * 3 + ('shield',) * 3,
                        b_faces=('helmet',) * 3 + ('shield',) * 3)
        self.gods_phase(a_choice=("Heimdall", 3))
        # 3 topory + 3 z łaski przeciw 3 hełmom
        self.assertEqual(self.b.hp, 18)
        self.assertEqual(self.a.hp, 21)
        self.assertEqual(self.a.bonus_stats, {})

    def test_players_have_independent_gods(self):
        self.a.mana = self.b.mana = 10
        self.dice_phase()
        self.gods_phase(a_choice=("Thor", 1), b_choice=("Thor", 3))
        self.assertEqual(self.b.hp, 21 - 3)
        self.assertEqual(self.a.hp, 21 - 8)
        self.assertIsNot(self.a.gods[0], self.b.gods[0])


class TestTurnOrder(GameTestCase):
    def test_leader_alternates_between_rounds(self):
        self.assertEqual((self.game.leader, self.game.active_player), ("A", "A"))
        self.dice_phase()
        self.assertEqual(self.game.active_player, "A")  # kierujący wybiera boga pierwszy
        self.gods_phase()
        self.assertEqual((self.game.round, self.game.leader, self.game.active_player), (2, "B", "B"))

    def test_leader_attacks_first(self):
        self.a.hp = self.b.hp = 1
        self.dice_phase(a_faces=('arrow',) + ('helmet',) * 5, b_faces=('arrow',) + ('helmet',) * 5)
        self.gods_phase()
        self.assertEqual(self.game.winner, self.a)

    def test_leader_attacks_first_in_second_round(self):
        self.dice_phase()
        self.gods_phase()
        self.a.hp = self.b.hp = 1
        self.dice_phase(a_faces=('arrow',) + ('helmet',) * 5, b_faces=('arrow',) + ('helmet',) * 5)
        self.gods_phase()
        self.assertEqual(self.game.winner, self.b)

    def test_wrong_player_cannot_move(self):
        with self.assertRaises(GameError):
            self.game.confirm_dice("B", [])
        with self.assertRaises(GameError):
            self.game.choose_god("A", None, None)


class TestDice(GameTestCase):
    def test_last_throw_keeps_all_dice(self):
        for _ in range(2):
            self.game.confirm_dice("A", [])
            self.game.confirm_dice("B", [])
        self.game.confirm_dice("A", [])
        self.assertEqual(len(self.a.saved_dice), 6)
        self.assertEqual(self.a.rzuty, 0)

    def test_keeping_all_dice_ends_throws(self):
        self.keep_all(self.a, NEUTRAL)
        self.assertEqual(self.a.rzuty, 0)
        self.game.confirm_dice("B", [0])
        # A nie ma już rzutów, więc B rzuca dalej
        self.assertEqual(self.game.active_player, "B")
        self.assertEqual(len(self.b.rolled_dice), 5)

    def test_invalid_indexes_are_rejected(self):
        for selected in ([6], [-1], ["0"], None, [True]):
            with self.assertRaises(GameError, msg=repr(selected)):
                self.game.confirm_dice("A", selected)
        self.assertEqual(self.a.rzuty, 3)

    def test_duplicate_indexes_save_die_once(self):
        self.game.confirm_dice("A", [0, 0, 0])
        self.assertEqual(len(self.a.saved_dice), 1)


class TestLifecycle(GameTestCase):
    def finish_with_a_winning(self):
        self.b.hp = 1
        self.dice_phase(a_faces=('arrow',) + ('helmet',) * 5, b_faces=('helmet',) * 6)
        self.gods_phase()

    def test_game_stops_after_win(self):
        self.finish_with_a_winning()
        self.assertEqual(self.game.stage, "finished")
        self.assertIsNone(self.game.active_player)
        self.assertEqual(self.a.rolled_dice, [])
        with self.assertRaises(GameError):
            self.game.confirm_dice("A", [])
        self.assertEqual(self.game.return_data()["winner"], "A")

    def test_rematch_resets_and_loser_leads(self):
        self.finish_with_a_winning()
        self.game.rematch()
        a, b = self.game.players["A"], self.game.players["B"]
        self.assertEqual((a.hp, b.hp, a.mana), (21, 21, 0))
        self.assertEqual((self.game.stage, self.game.leader, self.game.round), ("dice", "B", 1))
        self.assertIsNone(self.game.winner)

    def test_rematch_only_after_finish(self):
        with self.assertRaises(GameError):
            self.game.rematch()

    def test_hp_is_never_shown_below_zero(self):
        self.b.hp = 1
        self.dice_phase(a_faces=('arrow',) * 6, b_faces=('helmet',) * 6)
        self.gods_phase()
        self.assertEqual(self.game.return_data()["players"][1]["HP"], 0)


class TestRegistration(unittest.TestCase):
    def test_third_player_and_duplicates_are_rejected(self):
        game = Game()
        game.register_player("A")
        with self.assertRaises(GameError):
            game.register_player("A")
        with self.assertRaises(GameError):
            game.register_player("   ")
        game.register_player("B")
        with self.assertRaises(GameError):
            game.register_player("C")
        self.assertEqual(list(game.players), ["A", "B"])


class TestManaTiming(GameTestCase):
    def test_dice_mana_is_in_pool_when_choosing_gods(self):
        self.a.mana = 1
        self.keep_all(self.a, ('mana+', 'mana', 'axe+', 'shield', 'shield', 'shield'))
        # w trakcie rzutów mana z kości jest jeszcze "w drodze"
        data = {p["name"]: p for p in self.game.return_data()["players"]}
        self.assertEqual((data["A"]["Mana"], data["A"]["mana_available"]), (1, 5))
        self.keep_all(self.b, NEUTRAL)
        self.assertEqual(self.game.stage, "gods")
        data = {p["name"]: p for p in self.game.return_data()["players"]}
        self.assertEqual((data["A"]["Mana"], data["A"]["mana_available"]), (5, 5))

    def test_mana_is_not_counted_twice(self):
        self.dice_phase(a_faces=('mana+',) + ('shield',) * 5)
        self.assertEqual(self.a.mana, 2)
        self.gods_phase()
        self.assertEqual(self.a.mana, 2)
        self.assertEqual(self.a.mana_available, 2)  # nowa runda, jeszcze bez kości


class TestLog(GameTestCase):
    maxDiff = None

    def events(self):
        return [(e["type"], e["params"]) for e in self.game.log]

    def test_round_is_logged(self):
        self.a.mana = 3
        self.dice_phase(a_faces=('arrow', 'arrow', 'mana+') + ('helmet',) * 3, b_faces=('shield',) + ('helmet',) * 5)
        self.gods_phase(a_choice=("Thor", 1))
        self.assertEqual(self.events(), [
            ("round_start", {"leader": "A"}),
            ("dice_summary", {"player": "A", "counts": {"axe": 0, "arrow": 2, "helmet": 3, "shield": 0}, "mana": 2}),
            ("dice_summary", {"player": "B", "counts": {"axe": 0, "arrow": 0, "helmet": 5, "shield": 1}, "mana": 0}),
            ("mana_collected", {"gains": [{"player": "A", "gained": 2, "total": 5}]}),
            ("god_chosen", {"player": "A", "god": "Thor", "level": 1, "cost": 3}),
            ("god_skipped", {"player": "B"}),
            ("god_effect", {"player": "A", "god": "Thor", "level": 1, "effect": "damage", "target": "B",
                            "value": 3, "stat": None, "hp": 18}),
            ("attack", {"attacker": "A", "defender": "B", "arrow": 2, "shield": 1, "axe": 0, "helmet": 5,
                        "dmg": 1, "hp": 17}),
            ("attack", {"attacker": "B", "defender": "A", "arrow": 0, "shield": 0, "axe": 0, "helmet": 3,
                        "dmg": 0, "hp": 21}),
            ("round_start", {"leader": "B"}),
        ])
        self.assertEqual({e["round"] for e in self.game.log}, {1, 2})
        self.assertEqual([e["kind"] for e in self.game.log][:6], ["round", "dice", "dice", "mana", "god", "god"])

    def test_dice_are_summarised_once_per_round(self):
        for _ in range(3):
            self.game.confirm_dice(self.game.active_player, [])
            self.game.confirm_dice(self.game.active_player, [])
        kinds = [e["kind"] for e in self.game.log]
        self.assertEqual(kinds.count("dice"), 2)

    def test_self_gods(self):
        self.a.mana = 5
        self.b.mana = 2
        self.dice_phase(a_faces=('axe',) + ('shield',) * 5, b_faces=('helmet', 'helmet') + ('shield',) * 4)
        self.gods_phase(a_choice=("Heimdall", 1), b_choice=("Freya", 1))
        effects = {p["god"]: p for t, p in self.events() if t == "god_effect"}
        self.assertEqual((effects["Heimdall"]["effect"], effects["Heimdall"]["stat"], effects["Heimdall"]["value"]),
                         ("bonus", "axe", 1))
        self.assertEqual((effects["Freya"]["target"], effects["Freya"]["hp"]), ("B", 23))
        attack = next(p for t, p in self.events() if t == "attack" and p["attacker"] == "A")
        self.assertEqual((attack["axe"], attack["helmet"], attack["dmg"]), (2, 2, 0))

    def test_god_without_mana_is_logged(self):
        self.a.mana = 3
        self.dice_phase()
        self.game.choose_god("A", "Thor", 1)
        self.a.mana = 1  # np. mana zmieniła się przed walką
        self.game.choose_god("B", None, None)
        self.assertIn(("god_failed", {"player": "A", "god": "Thor", "mana": 1, "cost": 3}), self.events())

    def test_win_and_rematch_clear_log(self):
        self.b.hp = 1
        self.dice_phase(a_faces=('arrow',) + ('helmet',) * 5, b_faces=('helmet',) * 6)
        self.gods_phase()
        self.assertEqual(self.events()[-1], ("win", {"winner": "A"}))
        self.assertEqual(self.game.return_data()["log"][-1]["kind"], "win")
        self.game.rematch()
        self.assertEqual(self.events(), [("round_start", {"leader": "B"})])

    def test_log_is_capped(self):
        for _ in range(Game.MAX_LOG + 20):
            self.game._log("x", "info")
        self.assertEqual(len(self.game.log), Game.MAX_LOG)


class TestErrorCodes(GameTestCase):
    def test_errors_carry_codes_and_params(self):
        with self.assertRaises(GameError) as ctx:
            self.game.confirm_dice("B", [])
        self.assertEqual(ctx.exception.to_dict(), {"code": "not_your_turn", "params": {}})
        self.dice_phase()
        with self.assertRaises(GameError) as ctx:
            self.game.choose_god("A", "Thor", 2)
        self.assertEqual(ctx.exception.to_dict(),
                         {"code": "not_enough_mana", "params": {"god": "Thor", "level": 2, "cost": 4, "mana": 0}})
        with self.assertRaises(GameError) as ctx:
            Game().register_player("A", ["Zeus"])
        self.assertEqual(ctx.exception.to_dict(), {"code": "unknown_god", "params": {"god": "Zeus"}})


class TestGodSelection(unittest.TestCase):
    def test_player_gets_chosen_gods_in_catalog_order(self):
        game = Game()
        player = game.register_player("A", ["Heimdall", "Thor"])
        self.assertEqual([g.name for g in player.gods], ["Thor", "Heimdall"])

    def test_default_is_first_gods_from_catalog(self):
        game = Game()
        player = game.register_player("A")
        self.assertEqual(len(player.gods), min(Game.GODS_PER_PLAYER, len(god_factory())))

    def test_invalid_selections_are_rejected(self):
        for names in ([], ["Thor", "Thor"], ["Zeus"], "Thor", [1], ["Thor", "Freya", "Heimdall", "Loki"]):
            with self.assertRaises(GameError, msg=repr(names)):
                Game().register_player("A", names)

    def test_only_chosen_gods_can_be_used(self):
        game = Game()
        a = game.register_player("A", ["Freya"])
        game.register_player("B")
        game.start()
        a.mana = 10
        for _ in range(3):
            game.confirm_dice(game.active_player, [])
            game.confirm_dice(game.active_player, [])
        with self.assertRaises(GameError):
            game.choose_god("A", "Thor", 1)
        game.choose_god("A", "Freya", 1)

    def test_rematch_keeps_chosen_gods(self):
        game = Game()
        a = game.register_player("A", ["Freya"])
        game.register_player("B", ["Thor", "Heimdall"])
        game.start()
        a.hp = 0
        game._check_winner()
        game.rematch()
        self.assertEqual([g.name for g in game.players["A"].gods], ["Freya"])
        self.assertEqual([g.name for g in game.players["B"].gods], ["Thor", "Heimdall"])

    def test_lobby_data_and_leaving(self):
        game = Game()
        game.register_player("A")
        lobby = game.lobby_data()
        self.assertEqual(lobby["players"], ["A"])
        self.assertEqual(lobby["max_gods"], Game.GODS_PER_PLAYER)
        self.assertEqual([g["name"] for g in lobby["gods"]], [g.name for g in god_factory()])
        self.assertTrue(game.remove_waiting_player("A"))
        self.assertEqual(game.lobby_data()["players"], [])
        game.register_player("A"); game.register_player("B"); game.start()
        self.assertFalse(game.remove_waiting_player("A"))


class TestGodData(unittest.TestCase):
    def test_gods_are_described_by_data(self):
        data = {g["name"]: g for g in Game().lobby_data()["gods"]}
        self.assertEqual(data["Thor"], {"name": "Thor", "effect": "damage", "values": [3, 5, 8], "stat": None,
                                        "mana_costs": [3, 4, 5], "level": None})
        self.assertEqual((data["Heimdall"]["effect"], data["Heimdall"]["stat"]), ("bonus", "axe"))


if __name__ == "__main__":
    unittest.main()
