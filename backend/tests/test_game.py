import random
import unittest

from die import Die
from game import Game, GameError
from god import god_factory


def dice(*faces):
    """Kości z listy nazw; sufiks '+' oznacza złotą obwódkę (mana), np. 'axe+'."""
    return [Die(face.rstrip('+'), face.endswith('+')) for face in faces]


NEUTRAL = ('shield',) * 6


class GameTestCase(unittest.TestCase):
    def setUp(self):
        self.game = Game(rng=random.Random(7))
        self.a = self.game.register_player("A")
        self.b = self.game.register_player("B")
        # w testach każdy gracz ma dostęp do wszystkich łask
        self.a.gods = god_factory()
        self.b.gods = god_factory()
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

    def events(self, event_type=None):
        return [(e["type"], e["params"]) for e in self.game.log
                if event_type is None or e["type"] == event_type]

    def effect(self, god):
        return next(p for t, p in self.events("god_effect") if p["god"] == god)

    def after_phase(self, phase, probe):
        """Wywołuje probe() zaraz po danej fazie walki, zanim runda się wyczyści."""
        seen = []
        original = self.game._run_phase

        def spy(current, *args):
            done = original(current, *args)
            if current == phase:
                seen.append(probe())
            return done
        self.game._run_phase = spy
        return seen


class TestGods(GameTestCase):
    def test_catalog_matches_wiki(self):
        gods = {god.name: god for god in god_factory()}
        self.assertEqual(len(gods), 20)
        self.assertEqual(gods["Thor"].mana_costs, [4, 8, 12])
        self.assertEqual(gods["Thor"].values, [2, 5, 8])
        self.assertEqual(gods["Var"].mana_costs, [10, 14, 18])
        self.assertEqual(len({god.effect for god in gods.values()}), 20)

    def test_god_costs_mana(self):
        self.a.mana = 4
        self.a.hp = 15
        self.dice_phase()
        self.gods_phase(a_choice=("Idun", 1))
        self.assertEqual(self.a.mana, 0)
        self.assertEqual(self.a.hp, 17)

    def test_cannot_choose_unaffordable_god(self):
        self.dice_phase()
        with self.assertRaises(GameError):
            self.game.choose_god("A", "Thor", 1)
        self.assertEqual(self.game.active_player, "A")
        self.assertIsNone(self.a.chosen_god)

    def test_gold_dice_count_towards_cost(self):
        self.a.mana = 1
        self.dice_phase(a_faces=('helmet+',) * 3 + ('shield',) * 3)
        self.assertEqual(self.a.mana_available, 4)
        self.gods_phase(a_choice=("Thor", 1))
        self.assertEqual(self.b.hp, 19)
        self.assertEqual(self.a.mana, 0)

    def test_player_can_skip_god(self):
        self.dice_phase()
        self.gods_phase()
        self.assertEqual(self.game.round, 2)

    def test_invalid_level_is_rejected(self):
        self.a.mana = 20
        self.dice_phase()
        for level in (0, 4, "2", True, 1.0, None):
            with self.assertRaises(GameError, msg=repr(level)):
                self.game.choose_god("A", "Thor", level)

    def test_unknown_god_is_rejected(self):
        self.dice_phase()
        with self.assertRaises(GameError):
            self.game.choose_god("A", "Zeus", 1)

    def test_players_have_independent_gods(self):
        self.a.mana = self.b.mana = 20
        self.dice_phase()
        self.gods_phase(a_choice=("Thor", 1), b_choice=("Thor", 3))
        self.assertEqual(self.b.hp, 21 - 2)
        self.assertEqual(self.a.hp, 21 - 8)
        self.assertIsNot(self.a.gods[0], self.b.gods[0])

    def test_bonuses_last_one_round(self):
        self.a.mana = 6
        self.dice_phase(a_faces=('arrow',) * 3 + ('helmet',) * 3)
        self.gods_phase(a_choice=("Skadi", 1))
        self.assertEqual(self.a.bonus_stats, {})
        self.assertEqual(self.a.shield_ignore, 0)


class TestHandDice(GameTestCase):
    def test_hand_steals_mana_from_opponent(self):
        self.b.mana = 5
        self.dice_phase(a_faces=('hand', 'hand') + ('shield',) * 4)
        self.assertEqual((self.a.mana, self.b.mana), (2, 3))
        self.assertIn(("mana_stolen", {"thief": "A", "victim": "B", "hands": 2, "amount": 2,
                                       "thief_total": 2, "victim_total": 3}), self.events())

    def test_hand_alone_gives_nothing_when_opponent_is_broke(self):
        self.dice_phase(a_faces=('hand',) * 6)
        self.assertEqual((self.a.mana, self.b.mana), (0, 0))
        self.assertEqual(self.events("mana_stolen")[0][1]["amount"], 0)

    def test_gold_is_collected_before_stealing(self):
        # B dostaje 2 many z obwódek, A od razu mu ją kradnie
        self.dice_phase(a_faces=('hand',) * 3 + ('shield',) * 3, b_faces=('axe+', 'arrow+') + ('shield',) * 4)
        self.assertEqual((self.a.mana, self.b.mana), (2, 0))

    def test_gold_hand_gives_and_steals(self):
        self.b.mana = 1
        self.dice_phase(a_faces=('hand+',) + ('shield',) * 5)
        self.assertEqual((self.a.mana, self.b.mana), (2, 0))

    def test_leader_steals_first(self):
        self.a.mana = 1
        self.dice_phase(a_faces=('hand',) + ('shield',) * 5, b_faces=('hand', 'hand') + ('shield',) * 4)
        # A kradnie z pustej puli B, potem B zabiera A obie many
        self.assertEqual((self.a.mana, self.b.mana), (0, 1))
        self.assertEqual([p["amount"] for _, p in self.events("mana_stolen")], [0, 1])


class TestFavors(GameTestCase):
    """Po jednym teście na każdą łaskę z wiki."""

    def test_thor_strike(self):
        self.a.mana = 4
        self.dice_phase()
        self.gods_phase(a_choice=("Thor", 1))
        self.assertEqual(self.b.hp, 19)
        self.assertEqual(self.effect("Thor")["effect"], "thor_strike")

    def test_thor_can_finish_the_game(self):
        self.a.mana = 4
        self.b.hp = 2
        self.dice_phase()
        self.gods_phase(a_choice=("Thor", 1))
        self.assertEqual(self.game.winner, self.a)

    def test_idun_heals_up_to_max_hp(self):
        self.a.mana = 4
        self.a.hp = 20
        self.dice_phase()
        self.gods_phase(a_choice=("Idun", 1))
        self.assertEqual(self.a.hp, 21)
        self.assertEqual(self.effect("Idun")["healed"], 1)

    def test_vidar_removes_helmets(self):
        self.a.mana = 2
        self.dice_phase(a_faces=('axe',) * 3 + ('shield',) * 3, b_faces=('helmet',) * 3 + ('shield',) * 3)
        self.gods_phase(a_choice=("Vidar", 1))
        self.assertEqual(self.b.hp, 21 - 2)

    def test_ullr_ignores_shields(self):
        self.a.mana = 2
        self.dice_phase(a_faces=('arrow',) * 3 + ('helmet',) * 3, b_faces=('shield',) * 3 + ('helmet',) * 3)
        self.gods_phase(a_choice=("Ullr", 1))
        self.assertEqual(self.b.hp, 21 - 2)

    def test_heimdall_heals_per_block(self):
        self.a.mana = 4
        self.a.hp = 10
        self.dice_phase(a_faces=('helmet', 'helmet') + ('shield',) * 4, b_faces=('axe', 'axe') + ('shield',) * 4)
        self.gods_phase(a_choice=("Heimdall", 1))
        self.assertEqual(self.a.hp, 12)
        self.assertEqual(self.effect("Heimdall")["blocked"], 2)

    def test_baldr_doubles_defence(self):
        self.a.mana = 3
        self.dice_phase(a_faces=('helmet', 'helmet', 'arrow', 'arrow', 'arrow', 'arrow'),
                        b_faces=('axe',) * 4 + ('shield',) * 2)
        self.gods_phase(a_choice=("Baldr", 1))
        self.assertEqual(self.a.hp, 21)
        self.assertEqual(self.effect("Baldr")["helmets"], 2)

    def test_brunhild_multiplies_axes_rounding_up(self):
        self.a.mana = 6
        self.dice_phase(a_faces=('axe',) * 3 + ('shield',) * 3)
        self.gods_phase(a_choice=("Brunhild", 1))
        self.assertEqual(self.b.hp, 21 - 5)

    def test_freyr_boosts_majority_face(self):
        self.a.mana = 4
        self.dice_phase(a_faces=('axe', 'axe', 'arrow', 'shield', 'hand', 'helmet'))
        self.gods_phase(a_choice=("Freyr", 1))
        self.assertEqual(self.effect("Freyr")["stat"], "axe")
        self.assertEqual(self.b.hp, 21 - 4)   # strzała odbita przez tarcze B

    def test_hel_heals_for_axe_damage(self):
        self.a.mana = 6
        self.a.hp = 10
        self.dice_phase(a_faces=('axe',) * 3 + ('shield',) * 3)
        self.gods_phase(a_choice=("Hel", 1))
        self.assertEqual((self.a.hp, self.b.hp), (13, 18))

    def test_skadi_adds_arrows(self):
        self.a.mana = 6
        self.dice_phase(a_faces=('arrow', 'arrow') + ('helmet',) * 4, b_faces=('helmet',) * 6)
        self.gods_phase(a_choice=("Skadi", 1))
        self.assertEqual(self.b.hp, 21 - 4)

    def test_skuld_destroys_mana_per_arrow(self):
        self.a.mana = 4
        self.b.mana = 10
        self.dice_phase(a_faces=('arrow', 'arrow') + ('helmet',) * 4)
        self.gods_phase(a_choice=("Skuld", 1))
        self.assertEqual(self.b.mana, 6)

    def test_frigg_rerolls_chosen_dice(self):
        self.a.mana = 2
        self.dice_phase()
        before_a, before_b = list(self.a.saved_dice), list(self.b.saved_dice)
        seen = self.after_phase("before", lambda: (list(self.a.saved_dice), list(self.b.saved_dice)))
        self.gods_phase(a_choice=("Frigg", 1, {"targets": {"own": [0], "opponent": [5]}}))
        after_a, after_b = seen[0]
        self.assertIsNot(after_a[0], before_a[0])
        self.assertIsNot(after_b[5], before_b[5])
        self.assertEqual(after_a[1:], before_a[1:])
        self.assertEqual(self.effect("Frigg")["own"], 1)

    def test_frigg_target_count_is_limited(self):
        self.a.mana = 2
        self.dice_phase()
        for targets in ({"own": [0, 1, 2]}, {}, {"own": [9]}, {"own": [0, 0]}, {"opponent": ["1"]}, [0]):
            with self.assertRaises(GameError, msg=repr(targets)):
                self.game.choose_god("A", "Frigg", 1, {"targets": targets})
        self.assertIsNone(self.a.chosen_god)

    def test_loki_bans_opponent_dice(self):
        self.b.mana = 3
        self.dice_phase(a_faces=('helmet',) * 6, b_faces=('arrow', 'arrow') + ('helmet',) * 4)
        loki = self.b.find_god("Loki")
        with self.assertRaises(GameError) as ctx:
            loki.validate_choice(self.b, self.a, 1, {"targets": {"opponent": [0, 1]}})
        self.assertEqual(ctx.exception.to_dict(), {"code": "targets_count", "params": {"max": 1}})
        seen = self.after_phase("before", lambda: (self.a.saved_dice[0].banned, self.a.dice_stats["helmet"]))
        self.gods_phase(b_choice=("Loki", 1, {"targets": {"opponent": [0]}}))
        self.assertEqual(seen, [(True, 5)])

    def test_loki_ban_beats_opponent_arrows(self):
        self.a.mana = 3
        self.dice_phase(a_faces=('helmet',) * 6, b_faces=('arrow',) + ('helmet',) * 5)
        self.a.hp = 1
        self.gods_phase(a_choice=("Loki", 1, {"targets": {"opponent": [0]}}))
        self.assertIsNone(self.game.winner)
        self.assertEqual(self.a.hp, 1)

    def test_freyja_adds_dice(self):
        self.a.mana = 2
        self.dice_phase()
        seen = self.after_phase("before", lambda: len(self.a.saved_dice))
        self.gods_phase(a_choice=("Freyja", 1))
        self.assertEqual(seen, [7])
        self.assertEqual(len(self.effect("Freyja")["faces"]), 1)

    def test_mimir_gains_mana_per_damage(self):
        self.a.mana = 3
        self.dice_phase(b_faces=('axe',) * 3 + ('shield',) * 3)
        self.gods_phase(a_choice=("Mimir", 1))
        self.assertEqual((self.a.hp, self.a.mana), (18, 3))

    def test_bragi_gains_mana_per_hand(self):
        self.a.mana = 4
        self.dice_phase(a_faces=('hand', 'hand') + ('shield',) * 4)
        self.gods_phase(a_choice=("Bragi", 1))
        self.assertEqual(self.a.mana, 4)   # 4 - 4 za łaskę + 2 * 2 z rąk

    def test_odin_trades_health_for_mana(self):
        self.a.mana = 6
        self.dice_phase()
        self.gods_phase(a_choice=("Odin", 1, {"amount": 3}))
        self.assertEqual((self.a.hp, self.a.mana), (18, 9))

    def test_sacrifice_amount_is_validated(self):
        self.a.mana = 6
        self.dice_phase()
        for amount in (0, 21, "2", None, True):
            with self.assertRaises(GameError, msg=repr(amount)) as ctx:
                self.game.choose_god("A", "Odin", 1, {"amount": amount})
            self.assertEqual(ctx.exception.to_dict(), {"code": "invalid_amount", "params": {"max": 20}})

    def test_var_heals_per_opponent_mana_spent(self):
        self.a.mana = 10
        self.a.hp = 10
        self.b.mana = 4
        self.dice_phase()
        self.gods_phase(a_choice=("Var", 1), b_choice=("Thor", 1))
        self.assertEqual(self.a.hp, 10 - 2 + 4)

    def test_thrymr_lowers_opponent_favor(self):
        self.a.mana = 3
        self.b.mana = 8
        self.dice_phase()
        self.gods_phase(a_choice=("Thrymr", 1), b_choice=("Thor", 2))
        self.assertEqual(self.a.hp, 21 - 2)   # Thor zszedł z 2. na 1. poziom
        self.assertEqual(self.b.mana, 0)      # zapłacone za 2. poziom przepada
        self.assertEqual(self.effect("Thrymr")["new_level"], 1)

    def test_thrymr_can_cancel_favor(self):
        self.a.mana = 3
        self.b.mana = 4
        self.dice_phase()
        self.gods_phase(a_choice=("Thrymr", 1), b_choice=("Thor", 1))
        self.assertEqual(self.a.hp, 21)
        self.assertEqual(self.b.mana, 0)
        self.assertIn(("god_cancelled", {"player": "B", "god": "Thor", "cost": 4}), self.events())

    def test_tyr_trades_health_for_opponent_mana(self):
        self.a.mana = 4
        self.b.mana = 9
        self.dice_phase()
        self.gods_phase(a_choice=("Tyr", 1, {"amount": 2}))
        self.assertEqual((self.a.hp, self.b.mana), (19, 5))

    def test_favor_choice_is_visible_in_state(self):
        self.a.mana = 6
        self.dice_phase()
        self.game.choose_god("A", "Odin", 1, {"amount": 2})
        data = {p["name"]: p for p in self.game.return_data()["players"]}
        self.assertEqual(data["A"]["chosen_choice"], {"amount": 2})
        self.assertEqual(data["A"]["chosen_god"]["needs"], "amount")


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

    def test_dice_have_hand_instead_of_mana(self):
        self.assertIn("hand", Game.DICES)
        self.assertNotIn("mana", Game.DICES)


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
        self.b.mana = 1
        self.keep_all(self.a, ('hand+', 'hand', 'axe+', 'shield', 'shield', 'shield'))
        # w trakcie rzutów mana z obwódek jest jeszcze "w drodze"
        data = {p["name"]: p for p in self.game.return_data()["players"]}
        self.assertEqual((data["A"]["Mana"], data["A"]["mana_available"]), (1, 3))
        self.keep_all(self.b, NEUTRAL)
        self.assertEqual(self.game.stage, "gods")
        data = {p["name"]: p for p in self.game.return_data()["players"]}
        # 1 + 2 z obwódek + 1 skradziona B
        self.assertEqual((data["A"]["Mana"], data["A"]["mana_available"]), (4, 4))
        self.assertEqual(data["B"]["Mana"], 0)

    def test_mana_is_not_counted_twice(self):
        self.dice_phase(a_faces=('axe+',) + ('shield',) * 5)
        self.assertEqual(self.a.mana, 1)
        self.gods_phase()
        self.assertEqual(self.a.mana, 1)
        self.assertEqual(self.a.mana_available, 1)  # nowa runda, jeszcze bez kości


class TestLog(GameTestCase):
    maxDiff = None

    def test_round_is_logged(self):
        self.a.mana = 3
        self.dice_phase(a_faces=('arrow', 'arrow', 'hand+') + ('helmet',) * 3,
                        b_faces=('shield',) + ('helmet',) * 5)
        self.gods_phase(a_choice=("Thor", 1))
        self.assertEqual(self.events(), [
            ("round_start", {"leader": "A"}),
            ("dice_summary", {"player": "A", "counts": {"axe": 0, "arrow": 2, "helmet": 3, "shield": 0, "hand": 1},
                              "mana": 1}),
            ("dice_summary", {"player": "B", "counts": {"axe": 0, "arrow": 0, "helmet": 5, "shield": 1, "hand": 0},
                              "mana": 0}),
            ("mana_collected", {"gains": [{"player": "A", "gained": 1, "total": 4}]}),
            ("mana_stolen", {"thief": "A", "victim": "B", "hands": 1, "amount": 0, "thief_total": 4,
                             "victim_total": 0}),
            ("god_chosen", {"player": "A", "god": "Thor", "level": 1, "cost": 4}),
            ("god_skipped", {"player": "B"}),
            ("attack", {"attacker": "A", "defender": "B", "arrow": 2, "shield": 1, "axe": 0, "helmet": 5,
                        "dmg": 1, "blocked": 1, "axe_dmg": 0, "hp": 20}),
            ("attack", {"attacker": "B", "defender": "A", "arrow": 0, "shield": 0, "axe": 0, "helmet": 3,
                        "dmg": 0, "blocked": 0, "axe_dmg": 0, "hp": 21}),
            ("god_effect", {"player": "A", "god": "Thor", "effect": "thor_strike", "level": 1, "target": "B",
                            "value": 2, "hp": 18}),
            ("round_start", {"leader": "B"}),
        ])
        self.assertEqual({e["round"] for e in self.game.log}, {1, 2})
        self.assertEqual([e["kind"] for e in self.game.log][:7],
                         ["round", "dice", "dice", "mana", "mana", "god", "god"])

    def test_dice_are_summarised_once_per_round(self):
        for _ in range(3):
            self.game.confirm_dice(self.game.active_player, [])
            self.game.confirm_dice(self.game.active_player, [])
        kinds = [e["kind"] for e in self.game.log]
        self.assertEqual(kinds.count("dice"), 2)

    def test_before_favors_follow_priority(self):
        self.a.mana = 4
        self.b.mana = 2
        self.dice_phase(a_faces=('axe',) * 2 + ('shield',) * 4, b_faces=('helmet',) * 2 + ('shield',) * 4)
        # A kieruje, ale Vidar (B) ma pierwszeństwo przed Freyrem
        self.gods_phase(a_choice=("Freyr", 1), b_choice=("Vidar", 1))
        order = [p["god"] for _, p in self.events("god_effect")]
        self.assertEqual(order, ["Vidar", "Freyr"])

    def test_god_without_mana_is_logged(self):
        self.a.mana = 4
        self.dice_phase()
        self.game.choose_god("A", "Thor", 1)
        self.a.mana = 1  # np. mana zmieniła się przed walką
        self.game.choose_god("B", None, None)
        self.assertIn(("god_failed", {"player": "A", "god": "Thor", "mana": 1, "cost": 4}), self.events())

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
                         {"code": "not_enough_mana", "params": {"god": "Thor", "level": 2, "cost": 8, "mana": 0}})
        with self.assertRaises(GameError) as ctx:
            Game().register_player("A", ["Zeus"])
        self.assertEqual(ctx.exception.to_dict(), {"code": "unknown_god", "params": {"god": "Zeus"}})


class TestGodSelection(unittest.TestCase):
    def test_player_gets_chosen_gods_in_catalog_order(self):
        game = Game()
        player = game.register_player("A", ["Loki", "Thor"])
        self.assertEqual([g.name for g in player.gods], ["Thor", "Loki"])

    def test_default_is_first_gods_from_catalog(self):
        game = Game()
        player = game.register_player("A")
        self.assertEqual(len(player.gods), min(Game.GODS_PER_PLAYER, len(god_factory())))

    def test_invalid_selections_are_rejected(self):
        for names in ([], ["Thor", "Thor"], ["Zeus"], "Thor", [1], ["Thor", "Freyja", "Heimdall", "Loki"]):
            with self.assertRaises(GameError, msg=repr(names)):
                Game().register_player("A", names)

    def test_only_chosen_gods_can_be_used(self):
        game = Game()
        a = game.register_player("A", ["Freyja"])
        game.register_player("B")
        game.start()
        a.mana = 10
        for _ in range(3):
            game.confirm_dice(game.active_player, [])
            game.confirm_dice(game.active_player, [])
        with self.assertRaises(GameError):
            game.choose_god("A", "Thor", 1)
        game.choose_god("A", "Freyja", 1)

    def test_rematch_keeps_chosen_gods(self):
        game = Game()
        game.register_player("A", ["Freyja"])
        game.register_player("B", ["Thor", "Heimdall"])
        game.start()
        game.players["A"].hp = 0
        game._check_winner()
        game.rematch()
        self.assertEqual([g.name for g in game.players["A"].gods], ["Freyja"])
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
        self.assertEqual(data["Thor"], {"name": "Thor", "effect": "thor_strike", "values": [2, 5, 8],
                                        "mana_costs": [4, 8, 12], "phase": "after", "needs": None,
                                        "level": None})
        self.assertEqual(data["Odin"]["needs"], "amount")
        self.assertEqual(data["Loki"]["needs"], "opponent_dice")
        self.assertEqual(data["Frigg"]["needs"], "any_dice")


if __name__ == "__main__":
    unittest.main()
