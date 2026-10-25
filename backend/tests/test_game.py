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
        self.dice_phase(a_faces=('arrow', 'arrow') + ('helmet',) * 4, b_faces=('shield',) + ('helmet',) * 5)
        self.gods_phase(a_choice=("Thor", 1))
        log = self.texts()
        self.assertEqual(log[0], "Zaczyna A")
        self.assertIn("A odkłada: strzała, strzała, hełm, hełm, hełm, hełm", log)
        self.assertIn("B pomija łaskę", log)
        self.assertIn("A: Thor zadaje 3 obrażenia graczowi B (koszt 3 many, B ma 18 HP)", log)
        self.assertIn("A atakuje (strzały 2 na tarcze 1): 1 obrażenie, B ma 17 HP", log)
        self.assertIn("B nie ma czym atakować", log)
        self.assertEqual(log[-1], "Zaczyna B")
        self.assertEqual({e["round"] for e in self.game.log}, {1, 2})

    def test_reroll_and_last_throw(self):
        self.game.confirm_dice("A", [])
        self.assertEqual(self.texts()[-1], "A rzuca jeszcze raz wszystkimi kośćmi")
        self.b.rzuty = 1
        self.b.rolled_dice = dice('axe+', 'mana')
        self.game.confirm_dice("B", [])
        self.assertEqual(self.texts()[-1], "B bierze ostatni rzut: topór (+mana), mana")

    def test_heimdall_has_no_hp_info_and_failed_god_is_logged(self):
        self.a.mana = 5
        self.dice_phase()
        self.gods_phase(a_choice=("Heimdall", 3))
        self.assertIn("A: Heimdall daje +3 do toporów (koszt 5 many)", self.texts())

    def test_win_and_rematch_clear_log(self):
        self.b.hp = 1
        self.dice_phase(a_faces=('arrow',) + ('helmet',) * 5, b_faces=('helmet',) * 6)
        self.gods_phase()
        self.assertEqual(self.texts()[-1], "A wygrywa!")
        self.assertEqual(self.game.return_data()["log"][-1]["kind"], "win")
        self.game.rematch()
        self.assertEqual(self.texts(), ["Zaczyna B"])

    def test_log_is_capped(self):
        for _ in range(Game.MAX_LOG + 20):
            self.game._log("x")
        self.assertEqual(len(self.game.log), Game.MAX_LOG)


class TestPolish(unittest.TestCase):
    def test_damage_forms(self):
        from pl import damage
        self.assertEqual([damage(n) for n in (0, 1, 2, 5, 12, 22)],
                         ["0 obrażeń", "1 obrażenie", "2 obrażenia", "5 obrażeń", "12 obrażeń", "22 obrażenia"])


if __name__ == "__main__":
    unittest.main()
