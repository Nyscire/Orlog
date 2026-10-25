from __future__ import annotations
from typing import Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from player import Player


LEVELS = (1, 2, 3)

# Rodzaje efektów łask. Opis boga i wpis w dzienniku tworzy frontend
# na podstawie efektu i wartości, w języku wybranym przez gracza.
DAMAGE = "damage"   # obrażenia dla przeciwnika
HEAL = "heal"       # leczenie siebie
BONUS = "bonus"     # dodatkowe kości danego rodzaju (stat) w tej rundzie
EFFECTS = (DAMAGE, HEAL, BONUS)


class God:
    def __init__(self, name: str, effect: str, values: List[int], mana_costs: List[int],
                 stat: Optional[str] = None) -> None:
        if effect not in EFFECTS:
            raise ValueError(f"Nieznany efekt łaski: {effect}")
        if effect == BONUS and stat is None:
            raise ValueError("Efekt bonus wymaga rodzaju kości (stat)")
        self.name: str = name
        self.effect: str = effect
        self.values: List[int] = values
        self.mana_costs: List[int] = mana_costs
        self.stat: Optional[str] = stat

    @property
    def targets_opponent(self) -> bool:
        return self.effect == DAMAGE

    def cost(self, level: int) -> int:
        return self.mana_costs[level - 1]

    def value(self, level: int) -> int:
        return self.values[level - 1]

    def activate(self, target: Player, level: int) -> Dict[str, object]:
        """Działa na gracza i zwraca, co się stało (do dziennika)."""
        value = self.value(level)
        if self.effect == DAMAGE:
            target.hp -= value
        elif self.effect == HEAL:
            target.hp += value
        else:
            target.add_bonus(self.stat, value)
        return {"effect": self.effect, "target": target.name, "value": value,
                "stat": self.stat, "hp": max(target.hp, 0)}

    def return_data(self, level: Optional[int] = None) -> Dict[str, object]:
        return {"name": self.name,
                "effect": self.effect,
                "values": self.values,
                "stat": self.stat,
                "mana_costs": self.mana_costs,
                "level": level}

    def __str__(self) -> str:
        return f"{self.name} ({self.effect} {self.values}, koszt {self.mana_costs})"


def god_factory() -> List[God]:
    return [
        God("Thor", DAMAGE, [3, 5, 8], [3, 4, 5]),
        God("Freya", HEAL, [2, 5, 9], [2, 3, 5]),
        God("Heimdall", BONUS, [1, 2, 3], [2, 3, 5], stat="axe"),
        # God("Loki", BONUS, [1, 2, 3], [2, 3, 5], stat="helmet"),
    ]
