import logging
import random
from typing import Dict, List, Optional

from die import Die
from god import LEVELS, TARGET_OPPONENT, god_factory
from player import Player

log = logging.getLogger(__name__)


class GameError(Exception):
    """Ruch niezgodny z zasadami albo stanem gry. Komunikat trafia do gracza."""


class Game:
    DICES = ['axe', 'arrow', 'helmet', 'mana', 'shield']
    MAX_PLAYERS = 2
    MAX_NAME_LENGTH = 20

    # Fazy gry: "waiting" -> ("dice" -> "gods" -> walka)* -> "finished"
    def __init__(self, rng: Optional[random.Random] = None) -> None:
        self.players: Dict[str, Player] = {}
        self.round: int = 1
        self.leader: Optional[str] = None          # gracz kierujący w tej rundzie
        self.active_player: Optional[str] = None   # gracz, który teraz wykonuje ruch
        self.stage: str = "waiting"
        self.winner: Optional[Player] = None
        self.rng = rng or random.Random()

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
        raise GameError("Brak przeciwnika.")

    def _require_turn(self, player_name: str, stage: str) -> Player:
        if self.stage == "finished":
            raise GameError("Gra już się zakończyła.")
        if self.stage != stage:
            raise GameError("To nie jest ta faza gry.")
        if player_name != self.active_player:
            raise GameError("To nie jest Twoja tura.")
        return self.players[player_name]

    # ---------- lobby ----------

    def register_player(self, name: str) -> Player:
        name = (name or "").strip()
        if not name:
            raise GameError("Podaj nazwę gracza.")
        if len(name) > self.MAX_NAME_LENGTH:
            raise GameError(f"Nazwa może mieć najwyżej {self.MAX_NAME_LENGTH} znaków.")
        if name in self.players:
            raise GameError("Ta nazwa jest już zajęta.")
        if self.is_full:
            raise GameError("Gra jest już pełna.")
        player = Player(name, god_factory())
        self.players[name] = player
        return player

    def start(self) -> None:
        if not self.can_start:
            raise GameError("Gra nie może się jeszcze zacząć.")
        self.leader = next(iter(self.players))
        self._begin_round()

    def rematch(self) -> None:
        """Nowa partia z tymi samymi graczami; zaczyna przegrany."""
        if self.stage != "finished" or self.winner is None:
            raise GameError("Partia jeszcze trwa.")
        loser = self.opponent_of(self.winner)
        self.players = {name: Player(name, god_factory()) for name in self.players}
        self.round = 1
        self.winner = None
        self.leader = loser.name
        self._begin_round()

    # ---------- rundy ----------

    def _begin_round(self) -> None:
        for player in self.players.values():
            player.reset_round()
        self.stage = "dice"
        self.active_player = self.leader
        self.roll_dice(self.players[self.leader])

    def roll_dice(self, player: Player) -> None:
        player.rolled_dice = [
            Die(self.rng.choice(self.DICES), self.rng.choice([True, False]))
            for _ in range(Player.DICE_COUNT - len(player.saved_dice))
        ]

    def confirm_dice(self, player_name: str, selected: List[int]) -> None:
        player = self._require_turn(player_name, "dice")
        if not isinstance(selected, list) or any(type(i) is not int for i in selected):
            raise GameError("Nieprawidłowy wybór kości.")
        indexes = set(selected)
        if any(i < 0 or i >= len(player.rolled_dice) for i in indexes):
            raise GameError("Nieprawidłowy wybór kości.")
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

    def choose_god(self, player_name: str, god_name: Optional[str], level: Optional[int]) -> None:
        player = self._require_turn(player_name, "gods")
        if god_name is None:
            player.choose_god(None, None)  # gracz pomija łaskę w tej rundzie
        else:
            god = player.find_god(god_name) if isinstance(god_name, str) else None
            if god is None:
                raise GameError("Nie ma takiego boga.")
            if type(level) is not int or level not in LEVELS:
                raise GameError("Poziom łaski musi wynosić 1, 2 lub 3.")
            cost = god.cost(level)
            if cost > player.mana_available:
                raise GameError(f"Za mało many: {god.name} na poziomie {level} kosztuje {cost}, "
                                f"a masz {player.mana_available}.")
            player.choose_god(god, level)

        if player.name == self.leader:
            self.active_player = self.opponent_of(player).name
        else:
            self.battle()

    # ---------- walka ----------

    def battle(self) -> None:
        leader = self.players[self.leader]
        other = self.opponent_of(leader)
        order = [leader, other]

        for player in order:
            player.mana += player.dice_stats["mana"]

        for player in order:
            self._activate_god(player)
            if self._check_winner():
                return

        for attacker in order:
            attacker.attack(self.opponent_of(attacker))
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
            log.info("%s: za mało many na %s (%d/%d), łaska przepada", player.name, god.name, player.mana, cost)
            return
        player.mana -= cost
        target = self.opponent_of(player) if god.target == TARGET_OPPONENT else player
        god.activate(target, level)

    def _check_winner(self) -> bool:
        for player in self.players.values():
            if player.hp <= 0:
                self.winner = self.opponent_of(player)
                self.stage = "finished"
                self.active_player = None
                return True
        return False

    # ---------- stan dla klientów ----------

    def return_data(self) -> Dict[str, str | int | List | None]:
        return {"players": [player.return_data() for player in self.players.values()],
                "active_player": self.active_player,
                "leader": self.leader,
                "round": self.round,
                "stage": self.stage,
                "winner": self.winner.name if self.winner else None}
