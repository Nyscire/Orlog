from __future__ import annotations
from typing import Optional, List, Dict, TYPE_CHECKING


if TYPE_CHECKING:
    from player import Player


# Kogo dotyczy efekt łaski boga
TARGET_OPPONENT = "opponent"
TARGET_SELF = "self"

LEVELS = (1, 2, 3)


#TODO Dodać dynamiczne opisy
class God:
    def __init__(self, name: str, description: str, levels_description: List[str],
                 target: str, mana_costs: List[int], genitive: Optional[str] = None) -> None:
        self.name: str = name
        self.genitive: str = genitive or name   # "łaska Thora"
        self.target: str = target
        self.description: str = description
        self.levels_description: List[str] = levels_description
        self.mana_costs: List[int] = mana_costs

    def cost(self, level: int) -> int:
        return self.mana_costs[level - 1]

    def activate(self, target: Player, level: int) -> str:
        """Działa na gracza i zwraca opis efektu do dziennika,
        np. "Rywal traci 5 HP i ma teraz 16" albo "+2 do toporów w tej rundzie"."""
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
        return f"{target.name} traci {value} HP i ma teraz {max(target.hp, 0)}"


class Freya(God):
    VALUES = [2, 5, 9]

    def activate(self, target: Player, level: int) -> str:
        value = self.VALUES[level - 1]
        target.hp += value
        return f"odzyskuje {value} HP i ma teraz {target.hp}"


class Heimdall(God):
    VALUES = [1, 2, 3]

    def activate(self, target: Player, level: int) -> str:
        value = self.VALUES[level - 1]
        target.add_bonus("axe", value)
        return f"+{value} do toporów w tej rundzie"


class Loki(God):
    VALUES = [1, 2, 3]

    def activate(self, target: Player, level: int) -> str:
        value = self.VALUES[level - 1]
        target.add_bonus("helmet", value)
        return f"+{value} do hełmów w tej rundzie"


def god_factory() -> List[God]:
    gods: List[God] = []
    gods.append(Thor(
        "Thor",
        "Koszt many: 3 / 4 / 5\nZadaje przeciwnikowi 3 / 5 / 8 obrażeń.",
        ["3 obrażenia (3 many)", "5 obrażeń (4 many)", "8 obrażeń (5 many)"],
        TARGET_OPPONENT,
        [3, 4, 5],
        genitive="Thora",
    ))

    gods.append(Freya(
        "Freya",
        "Koszt many: 2 / 3 / 5\nPrzywraca ci 2 / 5 / 9 HP.",
        ["+2 HP (2 many)", "+5 HP (3 many)", "+9 HP (5 many)"],
        TARGET_SELF,
        [2, 3, 5],
        genitive="Freyi",
    ))

    gods.append(Heimdall(
        "Heimdall",
        "Koszt many: 2 / 3 / 5\nDodaje 1 / 2 / 3 topory do ataku w tej rundzie.",
        ["+1 topór (2 many)", "+2 topory (3 many)", "+3 topory (5 many)"],
        TARGET_SELF,
        [2, 3, 5],
        genitive="Heimdalla",
    ))

    # gods.append(Loki(
    #     "Loki",
    #     "Koszt many: 2 / 3 / 5\nDodaje 1 / 2 / 3 hełmy do obrony w tej rundzie.",
    #     ["+1 hełm (2 many)", "+2 hełmy (3 many)", "+3 hełmy (5 many)"],
    #     TARGET_SELF,
    #     [2, 3, 5],
    #     genitive="Lokiego",
    # ))

    return gods
