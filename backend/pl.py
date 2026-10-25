"""Drobne pomocnicze rzeczy do polskich tekstów w dzienniku gry."""

DIE_NAMES = {
    "axe": "topór",
    "arrow": "strzała",
    "helmet": "hełm",
    "shield": "tarcza",
    "mana": "mana",
}


def plural(n: int, one: str, few: str, many: str) -> str:
    """plural(1, 'kość', 'kości', 'kości') -> 'kość'; polska odmiana po liczebniku."""
    if n == 1:
        return one
    if n % 10 in (2, 3, 4) and n % 100 not in (12, 13, 14):
        return few
    return many


def damage(n: int) -> str:
    return f"{n} {plural(n, 'obrażenie', 'obrażenia', 'obrażeń')}"
