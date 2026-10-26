from typing import Dict


class Die:
    """Kość odłożona albo wylosowana przez gracza.

    stat: axe, arrow, helmet, shield albo hand (dłoń kradnie manę przeciwnikowi).
    gives_mana: złota obwódka, daje 1 manę.
    banned: kość zablokowana w tej rundzie (Sztuczka Lokiego), nie liczy się w walce.
    """

    def __init__(self, stat: str, gives_mana: bool) -> None:
        self.stat = stat
        self.gives_mana = gives_mana
        self.banned = False

    def return_data(self) -> Dict[str, object]:
        return {"stat": self.stat, "gives_mana": self.gives_mana, "banned": self.banned}

    def __repr__(self) -> str:
        return f"DIE [{self.stat} {self.gives_mana}{' banned' if self.banned else ''}]"
