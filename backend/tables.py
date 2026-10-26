"""Stoły: wiele partii naraz na jednym serwerze.

Każdy stół ma własną grę (Game) dla dwóch graczy. Gracz zakłada stół albo
dosiada się do stołu z listy. Przy stole dostaje token, dzięki któremu po
odświeżeniu strony wraca na swoje miejsce.

Ta klasa nie wie nic o Socket.IO: dostaje identyfikatory połączeń (sid)
i zwraca stoły, które się zmieniły. Wysyłaniem zajmuje się main.py.
"""
from __future__ import annotations

import random
import secrets
import time
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple

from errors import GameError
from game import Game
from god import god_factory

# znaki kodu stołu bez łatwych do pomylenia (0/O, 1/I/L)
CODE_ALPHABET = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"


@dataclass
class Seat:
    """Miejsce gracza przy stole."""
    name: str
    table_id: str
    token: str
    sid: Optional[str] = None             # aktualne połączenie; None, gdy gracz jest offline
    offline_since: Optional[float] = None


@dataclass
class Table:
    id: str
    name: Optional[str]                   # bez nazwy frontend pisze „Stół gracza X”
    host: str
    game: Game
    created_at: float
    # ostatnie zdarzenie przy stole, np. {"code": "player_left", "params": {"name": "Bjorn"}}
    notice: Optional[Dict[str, object]] = None
    seats: List[str] = field(default_factory=list)   # imiona w kolejności siadania

    @property
    def stage(self) -> str:
        return self.game.stage


class TableManager:
    MAX_TABLES = 50
    MAX_TABLE_NAME = 30
    WAITING_GRACE = 30      # s: tyle czeka miejsce gracza, który rozłączył się przed startem
    ABANDONED_GRACE = 300   # s: tyle trwa partia, w której nikt nie jest połączony

    def __init__(self, rng: Optional[random.Random] = None,
                 clock: Callable[[], float] = time.monotonic) -> None:
        self.rng = rng or random.Random()
        self.clock = clock
        self.tables: Dict[str, Table] = {}
        self.seats: Dict[str, Seat] = {}      # imię -> miejsce
        self.sids: Dict[str, str] = {}        # sid -> imię

    # ---------- pomocnicze ----------

    def _new_code(self) -> str:
        while True:
            code = "".join(self.rng.choice(CODE_ALPHABET) for _ in range(4))
            if code not in self.tables:
                return code

    def _new_game(self) -> Game:
        return Game(rng=random.Random(self.rng.random()))

    def _check_free_sid(self, sid: str) -> None:
        name = self.sids.get(sid)
        if name is not None:
            raise GameError("already_seated", name=name)

    def _check_name(self, name) -> str:
        if not isinstance(name, str) or not name.strip():
            raise GameError("name_required")
        name = name.strip()
        if len(name) > Game.MAX_NAME_LENGTH:
            raise GameError("name_too_long", max=Game.MAX_NAME_LENGTH)
        if name in self.seats:
            raise GameError("name_taken")
        return name

    def _sit(self, sid: str, table: Table, name: str, gods) -> Seat:
        table.game.register_player(name, gods)
        seat = Seat(name=name, table_id=table.id, token=secrets.token_urlsafe(16), sid=sid)
        self.seats[name] = seat
        self.sids[sid] = name
        table.seats.append(name)
        if table.game.can_start:
            table.notice = None
            table.game.start()
        return seat

    def _drop_seat(self, name: str) -> None:
        seat = self.seats.pop(name, None)
        if seat and seat.sid:
            self.sids.pop(seat.sid, None)

    def _remove_table(self, table: Table) -> None:
        for name in list(table.seats):
            self._drop_seat(name)
        self.tables.pop(table.id, None)

    def is_connected(self, name: str) -> bool:
        seat = self.seats.get(name)
        return bool(seat and seat.sid)

    def seat_of(self, sid: str) -> Optional[Seat]:
        name = self.sids.get(sid)
        return self.seats.get(name) if name else None

    def table_of(self, sid: str) -> Optional[Tuple[Table, str]]:
        seat = self.seat_of(sid)
        if seat is None:
            return None
        return self.tables[seat.table_id], seat.name

    def is_open(self, table: Table) -> bool:
        """Czy można się dosiąść: jest wolne miejsce, a czekający gracz jest połączony."""
        return (table.stage == "waiting" and not table.game.is_full
                and all(self.is_connected(name) for name in table.seats))

    # ---------- siadanie i wstawanie ----------

    def create_table(self, sid: str, name, gods=None, table_name=None) -> Seat:
        self._check_free_sid(sid)
        name = self._check_name(name)
        if table_name is not None and not isinstance(table_name, str):
            raise GameError("invalid_table_name")
        table_name = (table_name or "").strip() or None
        if table_name and len(table_name) > self.MAX_TABLE_NAME:
            raise GameError("table_name_too_long", max=self.MAX_TABLE_NAME)
        if len(self.tables) >= self.MAX_TABLES:
            raise GameError("too_many_tables", max=self.MAX_TABLES)
        table = Table(id=self._new_code(), name=table_name, host=name,
                      game=self._new_game(), created_at=self.clock())
        self.tables[table.id] = table
        try:
            return self._sit(sid, table, name, gods)
        except GameError:
            # np. błędny wybór bogów: nie zostawiamy pustego stołu
            del self.tables[table.id]
            raise

    def join_table(self, sid: str, table_id, name, gods=None) -> Seat:
        self._check_free_sid(sid)
        name = self._check_name(name)
        table = self.tables.get(table_id) if isinstance(table_id, str) else None
        if table is None:
            raise GameError("table_not_found")
        if not self.is_open(table):
            raise GameError("table_full" if table.game.is_full or table.stage != "waiting"
                            else "table_not_found")
        return self._sit(sid, table, name, gods)

    def resume(self, sid: str, name, token) -> Tuple[Seat, Optional[str]]:
        """Powrót na swoje miejsce (odświeżenie strony, zerwane połączenie).

        Zwraca miejsce i poprzednie połączenie, jeśli gracz był jeszcze
        podłączony w innej karcie (ta karta traci miejsce).
        """
        seat = self.seats.get(name) if isinstance(name, str) else None
        if seat is None or not isinstance(token, str) or not secrets.compare_digest(seat.token, token):
            raise GameError("seat_not_found")
        current = self.sids.get(sid)
        if current is not None and current != name:
            raise GameError("already_seated", name=current)
        previous = seat.sid if seat.sid != sid else None
        if previous:
            self.sids.pop(previous, None)
        seat.sid = sid
        seat.offline_since = None
        self.sids[sid] = name
        return seat, previous

    def leave(self, sid: str) -> Optional[Tuple[Optional[Table], str]]:
        """Gracz wstaje od stołu. Zwraca stół (None, jeśli zniknął) i imię gracza.

        Jeśli partia trwała albo się skończyła, przeciwnik zostaje przy stole
        i czeka na nowego rywala z tymi samymi bogami.
        """
        found = self.table_of(sid)
        if found is None:
            return None
        table, name = found
        self._remove_player(table, name)
        return (table if table.id in self.tables else None), name

    def _remove_player(self, table: Table, name: str) -> None:
        self._drop_seat(name)
        if name in table.seats:
            table.seats.remove(name)
        if not table.seats:
            self.tables.pop(table.id, None)
            return
        if table.stage == "waiting":
            table.game.remove_waiting_player(name)
            return
        # partia przerwana: zostaje świeża gra z pozostałym graczem
        rest = table.seats[0]
        gods = [god.name for god in table.game.players[rest].gods]
        table.game = self._new_game()
        table.game.register_player(rest, gods)
        table.host = rest
        table.notice = {"code": "player_left", "params": {"name": name}}

    def disconnect(self, sid: str) -> Optional[Table]:
        name = self.sids.pop(sid, None)
        seat = self.seats.get(name) if name else None
        if seat is None or seat.sid != sid:
            return None
        seat.sid = None
        seat.offline_since = self.clock()
        return self.tables.get(seat.table_id)

    def sweep(self) -> Tuple[List[Table], bool]:
        """Sprząta porzucone miejsca i stoły.

        Zwraca stoły, przy których ktoś został (do rozesłania stanu),
        i informację, czy zmieniła się lista stołów.
        """
        now = self.clock()
        changed: List[Table] = []
        list_changed = False
        for table in list(self.tables.values()):
            offline = {name: self.seats[name].offline_since for name in table.seats
                       if self.seats[name].offline_since is not None}
            if table.stage == "waiting":
                expired = [n for n, since in offline.items() if now - since >= self.WAITING_GRACE]
                for name in expired:
                    self._remove_player(table, name)
                    list_changed = True
                if expired and table.id in self.tables:
                    changed.append(table)
            elif len(offline) == len(table.seats) and \
                    all(now - since >= self.ABANDONED_GRACE for since in offline.values()):
                self._remove_table(table)
                list_changed = True
        return changed, list_changed

    # ---------- dane dla klientów ----------

    def table_summary(self, table: Table) -> Dict[str, object]:
        return {"id": table.id,
                "name": table.name,
                "host": table.host,
                "players": list(table.seats),
                "stage": table.stage,
                "round": table.game.round,
                "open": self.is_open(table)}

    def lobby_data(self) -> Dict[str, object]:
        """Lista stołów do menu: najpierw te z wolnym miejscem, potem trwające partie."""
        tables = [t for t in self.tables.values()
                  if t.stage != "waiting" or self.is_open(t)]
        tables.sort(key=lambda t: (not self.is_open(t), t.created_at))
        return {"tables": [self.table_summary(t) for t in tables],
                "gods": [god.return_data() for god in god_factory()],
                "max_gods": Game.GODS_PER_PLAYER,
                "max_tables": self.MAX_TABLES,
                "full": len(self.tables) >= self.MAX_TABLES}

    def state(self, table: Table) -> Dict[str, object]:
        """Stan gry przy stole, z informacją o stole i o tym, kto jest połączony."""
        data = table.game.return_data()
        for player in data["players"]:
            player["connected"] = self.is_connected(player["name"])
        data["table"] = {"id": table.id, "name": table.name, "host": table.host}
        data["notice"] = table.notice
        return data
