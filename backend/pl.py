"""Polskie teksty do dziennika gry: nazwy kości i odmiana po liczebniku."""

# mianownik: "2 topory"; biernik obrony: "na 1 tarczę"
DIE_FORMS = {
    "axe": ("topór", "topory", "toporów"),
    "arrow": ("strzała", "strzały", "strzał"),
    "helmet": ("hełm", "hełmy", "hełmów"),
    "shield": ("tarcza", "tarcze", "tarcz"),
}
DEFENCE_FORMS = {
    "helmet": ("hełm", "hełmy", "hełmów"),
    "shield": ("tarczę", "tarcze", "tarcz"),
}


def plural(n: int, one: str, few: str, many: str) -> str:
    """plural(1, 'kość', 'kości', 'kości') -> 'kość'; polska odmiana po liczebniku."""
    if n == 1:
        return one
    if n % 10 in (2, 3, 4) and n % 100 not in (12, 13, 14):
        return few
    return many


def count(n: int, forms: tuple) -> str:
    return f"{n} {plural(n, *forms)}"


def damage(n: int) -> str:
    return f"{n} {plural(n, 'obrażenie', 'obrażenia', 'obrażeń')}"
