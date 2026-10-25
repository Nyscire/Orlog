from __future__ import annotations

import logging
from typing import List, Optional, Dict
from god import God
from die import Die

log = logging.getLogger(__name__)

STATS = ("mana", "arrow", "axe", "shield", "helmet")


class Player:
    MAX_HP = 21
    DICE_COUNT = 6
    THROWS = 3

    def __init__(self, name: str, gods: List[God]) -> None:
        self.name: str = name
        self.hp: int = self.MAX_HP
        self.mana: int = 0
        self.rolled_dice: List[Die] = []
        self.saved_dice: List[Die] = []
        self.gods: List[God] = gods
        self.chosen_god: Optional[God] = None
        self.chosen_level: Optional[int] = None
        # Tymczasowe bonusy z łask bogów, ważne do końca rundy
        self.bonus_stats: Dict[str, int] = {}
        self.rzuty: int = self.THROWS
        # czy mana z kości tej rundy jest już w puli
        self.mana_collected: bool = False

    def find_god(self, god_name: str) -> Optional[God]:
        for god in self.gods:
            if god.name == god_name:
                return god
        return None

    def choose_dice(self, dice: List[int]) -> None:
        saved_dice = [elem for i, elem in enumerate(self.rolled_dice) if i in dice]
        self.saved_dice.extend(saved_dice)
        log.debug("%s: wylosowano %s, zatwierdzono %s", self.name, self.rolled_dice, saved_dice)
        self.rolled_dice = []
        self.rzuty -= 1
        # wszystkie kości zachowane, nie ma czym rzucać
        if len(self.saved_dice) >= self.DICE_COUNT:
            self.rzuty = 0

    def attack(self, enemy: Player) -> Dict[str, int]:
        my_stats = self.temp_stats
        enemy_stats = enemy.temp_stats

        arrow_dmg = max(my_stats["arrow"] - enemy_stats["shield"], 0)
        axe_dmg = max(my_stats["axe"] - enemy_stats["helmet"], 0)
        dmg = arrow_dmg + axe_dmg
        log.debug("%s atakuje %s: strzały %d, topory %d, razem %d",
                  self.name, enemy.name, arrow_dmg, axe_dmg, dmg)
        enemy.hp -= dmg
        return {"arrow": my_stats["arrow"], "shield": enemy_stats["shield"],
                "axe": my_stats["axe"], "helmet": enemy_stats["helmet"], "dmg": dmg}

    @property
    def can_roll(self) -> bool:
        return self.rzuty > 0

    @property
    def dice_stats(self) -> Dict[str, int]:
        """Statystyki wynikające wyłącznie z zachowanych kości."""
        stat_summary = {stat: 0 for stat in STATS}
        for die in self.saved_dice:
            stat_summary[die.stat] = stat_summary.get(die.stat, 0) + 1
            if die.gives_mana:
                stat_summary["mana"] += 1
        return stat_summary

    @property
    def temp_stats(self) -> Dict[str, int]:
        """Statystyki z kości powiększone o bonusy z łask bogów."""
        stat_summary = self.dice_stats
        for stat, value in self.bonus_stats.items():
            stat_summary[stat] = stat_summary.get(stat, 0) + value
        return stat_summary

    @property
    def mana_available(self) -> int:
        """Mana, którą gracz będzie miał w chwili aktywacji łaski (przed walką)."""
        return self.mana if self.mana_collected else self.mana + self.dice_stats["mana"]

    def collect_dice_mana(self) -> int:
        """Dodaje do puli manę z odłożonych kości (raz na rundę) i zwraca, ile jej było."""
        if self.mana_collected:
            return 0
        gained = self.dice_stats["mana"]
        self.mana += gained
        self.mana_collected = True
        return gained

    def add_bonus(self, stat: str, value: int) -> None:
        self.bonus_stats[stat] = self.bonus_stats.get(stat, 0) + value

    def choose_god(self, god: Optional[God], level: Optional[int]) -> None:
        self.chosen_god = god
        self.chosen_level = level if god else None

    def reset_round(self) -> None:
        self.rolled_dice = []
        self.saved_dice = []
        self.chosen_god = None
        self.chosen_level = None
        self.bonus_stats = {}
        self.rzuty = self.THROWS
        self.mana_collected = False

    def return_data(self) -> Dict[str, str | int | List | Dict | None]:
        if self.chosen_god:
            chosen_god_data = self.chosen_god.return_data(self.chosen_level)
        else:
            chosen_god_data = None
        return {"name": self.name,
                "HP": max(self.hp, 0),
                "Mana": self.mana,
                "mana_available": self.mana_available,
                "rzuty": self.rzuty,
                "rolled_dice": [die.return_data() for die in self.rolled_dice],
                "saved_dice": [die.return_data() for die in self.saved_dice],
                "gods": [god.return_data() for god in self.gods],
                "chosen_god": chosen_god_data}

    def __str__(self) -> str:
        return f"{self.name=}:{self.return_data()}"
