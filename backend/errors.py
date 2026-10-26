from typing import Dict


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
