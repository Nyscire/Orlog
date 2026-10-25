import random
from typing import Dict, List, Optional

from die import Die
from god import LEVELS, TARGET_OPPONENT, God, god_factory
from pl import DEFENCE_FORMS, DIE_FORMS, count, damage
from player import Player


class GameError(Exception):
    """Ruch niezgodny z zasadami albo stanem gry. Komunikat trafia do gracza."""


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
        # dziennik zdarzeń pokazywany graczom: {"round", "kind", "text"}
        self.log: List[Dict[str, str | int]] = []

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

    def _log(self, text: str, kind: str = "info") -> None:
        self.log.append({"round": self.round, "kind": kind, "text": text})
        del self.log[:-self.MAX_LOG]

    def _require_turn(self, player_name: str, stage: str) -> Player:
        if self.stage == "finished":
            raise GameError("Gra już się zakończyła.")
        if self.stage != stage:
            raise GameError("To nie jest ta faza gry.")
        if player_name != self.active_player:
            raise GameError("To nie jest Twoja tura.")
        return self.players[player_name]

    # ---------- lobby ----------

    @classmethod
    def pick_gods(cls, names: Optional[List[str]] = None) -> List[God]:
        """Bogowie wybrani przez gracza w menu; bez wyboru pierwsi z listy."""
        catalog = god_factory()
        if names is None:
            return catalog[:cls.GODS_PER_PLAYER]
        if not isinstance(names, list) or not all(isinstance(n, str) for n in names):
            raise GameError("Nieprawidłowy wybór bogów.")
        if len(set(names)) != len(names):
            raise GameError("Każdego boga można wybrać tylko raz.")
        if not 1 <= len(names) <= cls.GODS_PER_PLAYER:
            raise GameError(f"Wybierz od 1 do {cls.GODS_PER_PLAYER} bogów.")
        known = {god.name for god in catalog}
        for name in names:
            if name not in known:
                raise GameError(f"Nie ma boga {name}.")
        return [god for god in catalog if god.name in names]

    def register_player(self, name: str, god_names: Optional[List[str]] = None) -> Player:
        name = (name or "").strip()
        if not name:
            raise GameError("Podaj nazwę gracza.")
        if len(name) > self.MAX_NAME_LENGTH:
            raise GameError(f"Nazwa może mieć najwyżej {self.MAX_NAME_LENGTH} znaków.")
        if name in self.players:
            raise GameError("Ta nazwa jest już zajęta.")
        if self.is_full:
            raise GameError("Gra jest już pełna.")
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
            raise GameError("Gra nie może się jeszcze zacząć.")
        self.leader = next(iter(self.players))
        self._begin_round()

    def rematch(self) -> None:
        """Nowa partia z tymi samymi graczami; zaczyna przegrany."""
        if self.stage != "finished" or self.winner is None:
            raise GameError("Partia jeszcze trwa.")
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
        self._log(f"Zaczyna {self.leader}.", "round")
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
            # jeden wpis na gracza z tym, co ma na tę rundę, zamiast wpisu po każdym rzucie
            leader = self.players[self.leader]
            order = (leader, self.opponent_of(leader))
            for p in order:
                self._log(self._dice_summary(p), "dice")
            self._collect_mana(order)

    def _collect_mana(self, order) -> None:
        """Mana z kości trafia do puli od razu po rzutach, żeby było widać, ile można wydać na łaski."""
        gains = []
        for player in order:
            gained = player.collect_dice_mana()
            if gained:
                gains.append(f"{player.name} +{gained} (razem {player.mana})")
        if gains:
            self._log(f"Mana z kości trafia do puli: {', '.join(gains)}.", "mana")

    @staticmethod
    def _dice_summary(player: Player) -> str:
        stats = player.dice_stats
        parts = [count(stats[face], forms) for face, forms in DIE_FORMS.items() if stats[face]]
        text = f"{player.name}: {', '.join(parts) if parts else 'bez broni i obrony'}."
        if stats["mana"]:
            text += f" Mana z kości: {stats['mana']}."
        return text

    def choose_god(self, player_name: str, god_name: Optional[str], level: Optional[int]) -> None:
        player = self._require_turn(player_name, "gods")
        if god_name is None:
            player.choose_god(None, None)  # gracz pomija łaskę w tej rundzie
            self._log(f"{player.name} nie korzysta z łaski w tej rundzie.", "god")
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
            self._log(f"{player.name} wybiera łaskę {god.genitive}, poziom {level} (koszt {cost} many).", "god")

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
            self._log(f"{player.name} nie może użyć łaski {god.genitive}: za mało many ({player.mana} z {cost}).",
                      "battle")
            return
        player.mana -= cost
        target = self.opponent_of(player) if god.target == TARGET_OPPONENT else player
        effect = god.activate(target, level)
        self._log(f"{player.name} używa łaski {god.genitive}: {effect}.", "battle")

    def _log_attack(self, attacker: Player, defender: Player, result: Dict[str, int]) -> None:
        parts = []
        if result["arrow"]:
            parts.append(f"{count(result['arrow'], DIE_FORMS['arrow'])} na "
                         f"{count(result['shield'], DEFENCE_FORMS['shield'])}")
        if result["axe"]:
            parts.append(f"{count(result['axe'], DIE_FORMS['axe'])} na "
                         f"{count(result['helmet'], DEFENCE_FORMS['helmet'])}")
        if not parts:
            self._log(f"{attacker.name} nie atakuje: nie ma strzał ani toporów.", "battle")
            return
        hp = max(defender.hp, 0)
        if result["dmg"]:
            outcome = f"Zadaje {damage(result['dmg'])}, {defender.name} ma teraz {hp} HP."
        else:
            outcome = f"Obrona blokuje wszystko, {defender.name} ma nadal {hp} HP."
        self._log(f"{attacker.name} atakuje: {', '.join(parts)}. {outcome}", "battle")

    def _check_winner(self) -> bool:
        for player in self.players.values():
            if player.hp <= 0:
                self.winner = self.opponent_of(player)
                self.stage = "finished"
                self.active_player = None
                self._log(f"Koniec gry. Wygrywa {self.winner.name}.", "win")
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
