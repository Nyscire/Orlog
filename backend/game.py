import random
from typing import Dict, List, Optional

from die import Die
from god import LEVELS, God, god_factory
from player import Player


class GameError(Exception):
    """Ruch niezgodny z zasadami albo stanem gry.

    Niesie kod i parametry, a tekst w języku gracza tworzy frontend (errors.<kod>).
    """

    def __init__(self, code: str, **params) -> None:
        super().__init__(code)
        self.code = code
        self.params = params

    def to_dict(self) -> Dict[str, object]:
        return {"code": self.code, "params": self.params}


class Game:
    DICES = ['axe', 'arrow', 'helmet', 'mana', 'shield']
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
        self.players = {name: Player(name, self.pick_gods([g.name for g in p.gods]))
                        for name, p in self.players.items()}
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

    def roll_dice(self, player: Player) -> None:
        player.rolled_dice = [
            Die(self.rng.choice(self.DICES), self.rng.choice([True, False]))
            for _ in range(Player.DICE_COUNT - len(player.saved_dice))
        ]

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
                          counts={face: stats[face] for face in ("axe", "arrow", "helmet", "shield")},
                          mana=stats["mana"])
            self._collect_mana(order)

    def _collect_mana(self, order) -> None:
        """Mana z kości trafia do puli od razu po rzutach, żeby było widać, ile można wydać na łaski."""
        gains = []
        for player in order:
            gained = player.collect_dice_mana()
            if gained:
                gains.append({"player": player.name, "gained": gained, "total": player.mana})
        if gains:
            self._log("mana_collected", "mana", gains=gains)

    def choose_god(self, player_name: str, god_name: Optional[str], level: Optional[int]) -> None:
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
            player.choose_god(god, level)
            self._log("god_chosen", "god", player=player.name, god=god.name, level=level, cost=cost)

        if player.name == self.leader:
            self.active_player = self.opponent_of(player).name
        else:
            self.battle()

    # ---------- walka ----------

    def battle(self) -> None:
        leader = self.players[self.leader]
        other = self.opponent_of(leader)
        order = [leader, other]

        self._collect_mana(order)  # zwykle już zebrana po rzutach; tu tylko na wszelki wypadek

        for player in order:
            self._activate_god(player)
            if self._check_winner():
                return

        for attacker in order:
            defender = self.opponent_of(attacker)
            self._log_attack(attacker, defender, attacker.attack(defender))
            if self._check_winner():
                return

        self.round += 1
        self.leader = other.name
        self._begin_round()

    def _activate_god(self, player: Player) -> None:
        god, level = player.chosen_god, player.chosen_level
        if god is None or level is None:
            return
        cost = god.cost(level)
        if player.mana < cost:
            self._log("god_failed", "battle", player=player.name, god=god.name, mana=player.mana, cost=cost)
            return
        player.mana -= cost
        target = self.opponent_of(player) if god.targets_opponent else player
        result = god.activate(target, level)
        self._log("god_effect", "battle", player=player.name, god=god.name, level=level, **result)

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

    def lobby_data(self) -> Dict[str, object]:
        """Dane do menu startowego: dostępni bogowie i kto już jest w grze."""
        return {"gods": [god.return_data() for god in god_factory()],
                "max_gods": self.GODS_PER_PLAYER,
                "players": list(self.players),
                "stage": self.stage}

    def return_data(self) -> Dict[str, str | int | List | None]:
        return {"players": [player.return_data() for player in self.players.values()],
                "active_player": self.active_player,
                "leader": self.leader,
                "round": self.round,
                "stage": self.stage,
                "winner": self.winner.name if self.winner else None,
                "log": self.log}
