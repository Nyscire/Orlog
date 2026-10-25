from __future__ import annotations
from typing import Optional, List, Dict, TYPE_CHECKING

from pl import damage

if TYPE_CHECKING:
    from player import Player


# Kogo dotyczy efekt łaski boga
TARGET_OPPONENT = "opponent"
TARGET_SELF = "self"

LEVELS = (1, 2, 3)


#TODO Dodać dynamiczne opisy
class God:
    def __init__(self, name: str, description: str, levels_description: List[str],
                 target: str, mana_costs: List[int]) -> None:
        self.name: str = name
        self.target: str = target
        self.description: str = description
        self.levels_description: List[str] = levels_description
        self.mana_costs: List[int] = mana_costs

    def cost(self, level: int) -> int:
        return self.mana_costs[level - 1]

    def activate(self, target: Player, level: int) -> str:
        """Działa na gracza i zwraca opis efektu do dziennika."""
        raise NotImplementedError

    def return_data(self, level: Optional[int] = None) -> Dict[str, str | List | int | None]:
        return {"name": self.name,
                "description": self.description,
                "levels": self.levels_description,
                "mana_costs": self.mana_costs,
                "level": level}

    def __str__(self) -> str:
        return f"Name:{self.name}, description:{self.description},levels:{self.levels_description}"


class Thor(God):
    VALUES = [3, 5, 8]

    def activate(self, target: Player, level: int) -> str:
        value = self.VALUES[level - 1]
        target.hp -= value
        return f"Thor zadaje {damage(value)} graczowi {target.name}"


class Freya(God):
    VALUES = [2, 5, 9]

    def activate(self, target: Player, level: int) -> str:
        value = self.VALUES[level - 1]
        target.hp += value
        return f"Freya leczy o {value} HP"


class Heimdall(God):
    VALUES = [1, 2, 3]

    def activate(self, target: Player, level: int) -> str:
        value = self.VALUES[level - 1]
        target.add_bonus("axe", value)
        return f"Heimdall daje +{value} do toporów"


class Loki(God):
    VALUES = [1, 2, 3]

    def activate(self, target: Player, level: int) -> str:
        value = self.VALUES[level - 1]
        target.add_bonus("helmet", value)
        return f"Loki daje +{value} do hełmów"


def god_factory() -> List[God]:
    gods: List[God] = []
    gods.append(Thor(
        "Thor",
        "Koszt many: 3/4/5\nZadaj 3/5/8 obrażeń przeciwnikowi",
        ["3 many: 3 obrażenia", "4 many: 5 obrażeń", "5 many: 8 obrażeń"],
        TARGET_OPPONENT,
        [3, 4, 5]
    ))

    gods.append(Freya(
        "Freya",
        "Koszt many: 2/3/5\nUlecz się o 2/5/9 punkty życia",
        ["2 many: 2 HP", "3 many: 5 HP", "5 many: 9 HP"],
        TARGET_SELF,
        [2, 3, 5]
    ))

    gods.append(Heimdall(
        "Heimdall",
        "Koszt many: 2/3/5\nTymczasowo wzmocnij siłę toporów o 1/2/3 punkty",
        ["2 many: +1 topór", "3 many: +2 topory", "5 many: +3 topory"],
        TARGET_SELF,
        [2, 3, 5]
    ))

    # gods.append(Loki(
    #     "Loki",
    #     "Koszt many: 2/3/5\nTymczasowo wzmocnij siłę tarczy o 1/2/3 punkty",
    #     ["2 many: +1 tarcza", "3 many: +2 tarcze", "5 many: +3 tarcze"],
    #     TARGET_SELF,
    #     [2, 3, 5]
    # ))

    return gods
