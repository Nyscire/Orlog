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


class TestLog(GameTestCase):
    def texts(self):
        return [e["text"] for e in self.game.log]

    def test_round_is_logged(self):
        self.a.mana = 3
        self.dice_phase(a_faces=('arrow', 'arrow', 'mana+') + ('helmet',) * 3, b_faces=('shield',) + ('helmet',) * 5)
        self.gods_phase(a_choice=("Thor", 1))
        self.assertEqual(self.texts(), [
            "Zaczyna A.",
            "A: 2 strzały, 3 hełmy. Mana z kości: 2.",
            "B: 5 hełmów, 1 tarcza.",
            "A wybiera łaskę Thora, poziom 1 (koszt 3 many).",
            "B nie korzysta z łaski w tej rundzie.",
            "Mana z kości trafia do puli: A +2 (razem 5).",
            "A używa łaski Thora: B traci 3 HP i ma teraz 18.",
            "A atakuje: 2 strzały na 1 tarczę. Zadaje 1 obrażenie, B ma teraz 17 HP.",
            "B nie atakuje: nie ma strzał ani toporów.",
            "Zaczyna B.",
        ])
        self.assertEqual({e["round"] for e in self.game.log}, {1, 2})

    def test_dice_are_summarised_once_per_round(self):
        for _ in range(3):
            self.game.confirm_dice(self.game.active_player, [])
            self.game.confirm_dice(self.game.active_player, [])
        kinds = [e["kind"] for e in self.game.log]
        self.assertEqual(kinds.count("dice"), 2)

    def test_blocked_attack_and_self_gods(self):
        self.a.mana = 5
        self.b.mana = 2
        self.dice_phase(a_faces=('axe',) + ('shield',) * 5, b_faces=('helmet', 'helmet') + ('shield',) * 4)
        self.gods_phase(a_choice=("Heimdall", 1), b_choice=("Freya", 1))
        log = self.texts()
        self.assertIn("A używa łaski Heimdalla: +1 do toporów w tej rundzie.", log)
        self.assertIn("B używa łaski Freyi: odzyskuje 2 HP i ma teraz 23.", log)
        self.assertIn("A atakuje: 2 topory na 2 hełmy. Obrona blokuje wszystko, B ma nadal 23 HP.", log)

    def test_god_without_mana_is_logged(self):
        self.a.mana = 3
        self.dice_phase()
        self.game.choose_god("A", "Thor", 1)
        self.a.mana = 1  # np. mana zmieniła się przed walką
        self.game.choose_god("B", None, None)
        self.assertIn("A nie może użyć łaski Thora: za mało many (1 z 3).", self.texts())

    def test_win_and_rematch_clear_log(self):
        self.b.hp = 1
        self.dice_phase(a_faces=('arrow',) + ('helmet',) * 5, b_faces=('helmet',) * 6)
        self.gods_phase()
        self.assertEqual(self.texts()[-1], "Koniec gry. Wygrywa A.")
        self.assertEqual(self.game.return_data()["log"][-1]["kind"], "win")
        self.game.rematch()
        self.assertEqual(self.texts(), ["Zaczyna B."])

    def test_log_is_capped(self):
        for _ in range(Game.MAX_LOG + 20):
            self.game._log("x")
        self.assertEqual(len(self.game.log), Game.MAX_LOG)


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


class TestPolish(unittest.TestCase):
    def test_damage_forms(self):
        from pl import damage
        self.assertEqual([damage(n) for n in (0, 1, 2, 5, 12, 22)],
                         ["0 obrażeń", "1 obrażenie", "2 obrażenia", "5 obrażeń", "12 obrażeń", "22 obrażenia"])

    def test_dice_forms(self):
        from pl import DEFENCE_FORMS, DIE_FORMS, count
        self.assertEqual(count(1, DIE_FORMS["axe"]), "1 topór")
        self.assertEqual(count(5, DIE_FORMS["arrow"]), "5 strzał")
        self.assertEqual(count(1, DEFENCE_FORMS["shield"]), "1 tarczę")
        self.assertEqual(count(3, DEFENCE_FORMS["helmet"]), "3 hełmy")


if __name__ == "__main__":
    unittest.main()
