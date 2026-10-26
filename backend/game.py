import random
from typing import Dict, List, Optional

from die import Die
from errors import GameError
from god import AFTER, BEFORE, FIRST, LEVELS, FavorContext, God, god_factory
from player import FACES, Player

__all__ = ["Game", "GameError"]


class Game:
    DICES = ['axe', 'arrow', 'helmet', 'hand', 'shield']
    MAX_PLAYERS = 2
    MAX_NAME_LENGTH = 20
    MAX_LOG = 150
    GODS_PER_PLAYER = 3   # ilu bogów gracz zabiera do partii

    # Fazy gry: "waiting" -> ("dice" -> "gods" -> walka)* -> "finished"
    def __init__(self, rng: Optional[random.Random] = None) -> None:
        self.players: Dict[str, Player] = {}
        self.round: int = 1
        self.leader: Optional[str] = None          # gracz kierujący w tej rundzie
        self.active_player: Optional[str] = None   # gracz, który teraz wykonuje ruch
        self.stage: str = "waiting"
        self.winner: Optional[Player] = None
        self.rng = rng or random.Random()
        # dziennik zdarzeń: {"round", "kind", "type", "params"}; tekst tworzy frontend
        self.log: List[Dict[str, object]] = []

    # ---------- pomocnicze ----------

    @property
    def is_full(self) -> bool:
        return len(self.players) >= self.MAX_PLAYERS

    @property
    def can_start(self) -> bool:
        return self.is_full and self.stage == "waiting"

    def opponent_of(self, player: Player) -> Player:
        for other in self.players.values():
            if other is not player:
                return other
        raise GameError("no_opponent")

    def _log(self, event: str, kind: str, **params) -> None:
        self.log.append({"round": self.round, "kind": kind, "type": event, "params": params})
        del self.log[:-self.MAX_LOG]

    def _require_turn(self, player_name: str, stage: str) -> Player:
        if self.stage == "finished":
            raise GameError("game_finished")
        if self.stage != stage:
            raise GameError("wrong_stage")
        if player_name != self.active_player:
            raise GameError("not_your_turn")
        return self.players[player_name]

    # ---------- lobby ----------

    @classmethod
    def pick_gods(cls, names: Optional[List[str]] = None) -> List[God]:
        """Bogowie wybrani przez gracza w menu; bez wyboru pierwsi z listy."""
        catalog = god_factory()
        if names is None:
            return catalog[:cls.GODS_PER_PLAYER]
        if not isinstance(names, list) or not all(isinstance(n, str) for n in names):
            raise GameError("invalid_gods")
        if len(set(names)) != len(names):
            raise GameError("duplicate_gods")
        if not 1 <= len(names) <= cls.GODS_PER_PLAYER:
            raise GameError("gods_count", max=cls.GODS_PER_PLAYER)
        known = {god.name for god in catalog}
        for name in names:
            if name not in known:
                raise GameError("unknown_god", god=name)
        return [god for god in catalog if god.name in names]

    @staticmethod
    def _fresh_gods(gods: List[God]) -> List[God]:
        names = {god.name for god in gods}
        return [god for god in god_factory() if god.name in names]

    def register_player(self, name: str, god_names: Optional[List[str]] = None) -> Player:
        name = (name or "").strip()
        if not name:
            raise GameError("name_required")
        if len(name) > self.MAX_NAME_LENGTH:
            raise GameError("name_too_long", max=self.MAX_NAME_LENGTH)
        if name in self.players:
            raise GameError("name_taken")
        if self.is_full:
            raise GameError("game_full")
        player = Player(name, self.pick_gods(god_names))
        self.players[name] = player
        return player

    def remove_waiting_player(self, name: str) -> bool:
        """Wyjście z lobby przed startem gry."""
        if self.stage == "waiting" and name in self.players:
            del self.players[name]
            return True
        return False

    def start(self) -> None:
        if not self.can_start:
            raise GameError("cannot_start")
        self.leader = next(iter(self.players))
        self._begin_round()

    def rematch(self) -> None:
        """Nowa partia z tymi samymi graczami; zaczyna przegrany."""
        if self.stage != "finished" or self.winner is None:
            raise GameError("game_in_progress")
        loser = self.opponent_of(self.winner)
        # każdy zostaje przy bogach wybranych w menu
        self.players = {name: Player(name, self._fresh_gods(p.gods)) for name, p in self.players.items()}
        self.round = 1
        self.winner = None
        self.leader = loser.name
        self.log = []
        self._begin_round()

    # ---------- rundy ----------

    def _begin_round(self) -> None:
        for player in self.players.values():
            player.reset_round()
        self.stage = "dice"
        self.active_player = self.leader
        self._log("round_start", "round", leader=self.leader)
        self.roll_dice(self.players[self.leader])

    def random_die(self) -> Die:
        return Die(self.rng.choice(self.DICES), self.rng.choice([True, False]))

    def roll_dice(self, player: Player) -> None:
        player.rolled_dice = [self.random_die() for _ in range(Player.DICE_COUNT - len(player.saved_dice))]

    def confirm_dice(self, player_name: str, selected: List[int]) -> None:
        player = self._require_turn(player_name, "dice")
        if not isinstance(selected, list) or any(type(i) is not int for i in selected):
            raise GameError("invalid_dice")
        indexes = set(selected)
        if any(i < 0 or i >= len(player.rolled_dice) for i in indexes):
            raise GameError("invalid_dice")
        if player.rzuty == 1:
            # Ostatni rzut: zostają wszystkie wylosowane kości
            indexes = set(range(len(player.rolled_dice)))
        player.choose_dice(sorted(indexes))
        self._next_dice_turn(player)

    def _next_dice_turn(self, player: Player) -> None:
        opponent = self.opponent_of(player)
        if opponent.can_roll:
            self.active_player = opponent.name
            self.roll_dice(opponent)
        elif player.can_roll:
            self.roll_dice(player)
        else:
            self.stage = "gods"
            self.active_player = self.leader
            # jeden wpis na gracza z tym, co ma na tę rundę, zamiast wpisu po każdym rzucie
            leader = self.players[self.leader]
            order = (leader, self.opponent_of(leader))
            for p in order:
                stats = p.dice_stats
                self._log("dice_summary", "dice", player=p.name,
                          counts={face: stats[face] for face in FACES},
                          mana=stats["mana"])
            self._collect_mana(order)

    def _collect_mana(self, order) -> None:
        """Rozliczenie many zaraz po rzutach, żeby było widać, ile można wydać na łaski.

        Najpierw każdy dostaje manę ze złotych obwódek, potem ręce kradną
        po 1 manie przeciwnikowi (zaczyna gracz kierujący).
        """
        if all(player.mana_collected for player in order):
            return
        gains = []
        for player in order:
            gained = player.collect_gold_mana()
            if gained:
                gains.append({"player": player.name, "gained": gained, "total": player.mana})
        if gains:
            self._log("mana_collected", "mana", gains=gains)
        for thief in order:
            victim = self.opponent_of(thief)
            hands = thief.dice_stats["hand"]
            if not hands:
                continue
            stolen = min(hands, victim.mana)
            victim.mana -= stolen
            thief.mana += stolen
            self._log("mana_stolen", "mana", thief=thief.name, victim=victim.name, hands=hands,
                      amount=stolen, thief_total=thief.mana, victim_total=victim.mana)

    def choose_god(self, player_name: str, god_name: Optional[str], level: Optional[int],
                   choice: Optional[Dict] = None) -> None:
        player = self._require_turn(player_name, "gods")
        if god_name is None:
            player.choose_god(None, None)  # gracz pomija łaskę w tej rundzie
            self._log("god_skipped", "god", player=player.name)
        else:
            god = player.find_god(god_name) if isinstance(god_name, str) else None
            if god is None:
                raise GameError("unknown_god", god=str(god_name))
            if type(level) is not int or level not in LEVELS:
                raise GameError("invalid_level")
            cost = god.cost(level)
            if cost > player.mana_available:
                raise GameError("not_enough_mana", god=god.name, level=level, cost=cost,
                                mana=player.mana_available)
            if choice is not None and not isinstance(choice, dict):
                raise GameError("invalid_targets")
            checked = god.validate_choice(player, self.opponent_of(player), level, choice or {})
            player.choose_god(god, level, checked)
            self._log("god_chosen", "god", player=player.name, god=god.name, level=level, cost=cost,
                      **checked)

        if player.name == self.leader:
            self.active_player = self.opponent_of(player).name
        else:
            self.battle()

    # ---------- walka ----------

    def battle(self) -> None:
        """Rozliczenie rundy.

        1. Kradzież Thryma (płaci od razu i obniża poziom łaski przeciwnika).
        2. Zapłata za pozostałe łaski (pełny koszt wybranego poziomu).
        3. Łaski "przed walką" (kości i ich siła), według kolejności `order`.
        4. Ataki: topory na hełmy, strzały na tarcze.
        5. Łaski "po walce" (obrażenia, leczenie, mana).
        """
        leader = self.players[self.leader]
        other = self.opponent_of(leader)
        order = [leader, other]

        self._collect_mana(order)  # zwykle już zebrana po rzutach; tu tylko na wszelki wypadek

        stats = {p.name: {"blocked": 0, "axe_damage": 0, "damage_taken": 0, "spent": 0} for p in order}
        favors = {p.name: {"god": p.chosen_god, "level": p.chosen_level, "choice": p.chosen_choice,
                           "paid": False}
                  for p in order if p.chosen_god is not None and p.chosen_level}

        for player in order:
            favor = favors.get(player.name)
            if favor and favor["god"].phase == FIRST:
                if self._pay(player, favor, favors, stats):
                    self._apply_favor(player, favor, favors, stats)
                    favor["done"] = True

        for player in order:
            favor = favors.get(player.name)
            if favor and not favor["paid"]:
                self._pay(player, favor, favors, stats)

        if self._run_phase(BEFORE, order, favors, stats):
            return

        for attacker in order:
            defender = self.opponent_of(attacker)
            result = attacker.attack(defender)
            stats[defender.name]["blocked"] += result["blocked"]
            stats[defender.name]["damage_taken"] += result["dmg"]
            stats[attacker.name]["axe_damage"] += result["axe_dmg"]
            self._log_attack(attacker, defender, result)
            if self._check_winner():
                return

        if self._run_phase(AFTER, order, favors, stats):
            return

        self.round += 1
        self.leader = other.name
        self._begin_round()

    def _pay(self, player: Player, favor: Dict, favors: Dict, stats: Dict) -> bool:
        """Płaci za łaskę; bez many albo po Kradzieży Thryma łaska przepada."""
        god = favor["god"]
        cost = god.cost(player.chosen_level)  # płaci się za poziom wybrany przy stole
        if player.mana < cost:
            self._log("god_failed", "battle", player=player.name, god=god.name, mana=player.mana, cost=cost)
            del favors[player.name]
            return False
        player.mana -= cost
        stats[player.name]["spent"] += cost
        favor["paid"] = True
        if favor["level"] <= 0:
            self._log("god_cancelled", "battle", player=player.name, god=god.name, cost=cost)
            del favors[player.name]
            return False
        return True

    def _run_phase(self, phase: str, order: List[Player], favors: Dict, stats: Dict) -> bool:
        """Łaski z danej fazy; zwraca True, gdy gra się skończyła."""
        queue = [(favors[p.name]["god"].order, i, p) for i, p in enumerate(order)
                 if p.name in favors and favors[p.name]["god"].phase == phase
                 and not favors[p.name].get("done")]
        for _, _, player in sorted(queue, key=lambda item: item[:2]):
            self._apply_favor(player, favors[player.name], favors, stats)
            if self._check_winner():
                return True
        return False

    def _apply_favor(self, player: Player, favor: Dict, favors: Dict, stats: Dict) -> None:
        god, level = favor["god"], favor["level"]
        ctx = FavorContext(self, player, self.opponent_of(player), level, favor["choice"], favors, stats)
        result = god.apply(ctx)
        self._log("god_effect", "battle", player=player.name, god=god.name, effect=god.effect,
                  level=level, **result)

    def _log_attack(self, attacker: Player, defender: Player, result: Dict[str, int]) -> None:
        self._log("attack", "battle", attacker=attacker.name, defender=defender.name,
                  hp=max(defender.hp, 0), **result)

    def _check_winner(self) -> bool:
        for player in self.players.values():
            if player.hp <= 0:
                self.winner = self.opponent_of(player)
                self.stage = "finished"
                self.active_player = None
                self._log("win", "win", winner=self.winner.name)
                return True
        return False

    # ---------- stan dla klientów ----------

    def return_data(self) -> Dict[str, str | int | List | None]:
        return {"players": [player.return_data() for player in self.players.values()],
                "active_player": self.active_player,
                "leader": self.leader,
                "round": self.round,
                "stage": self.stage,
                "winner": self.winner.name if self.winner else None,
                "log": self.log}
