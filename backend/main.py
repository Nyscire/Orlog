"""Serwer gry: wiele stołów, przy każdym osobna partia dla dwóch graczy.

Każdy stół to pokój Socket.IO, więc stan gry trafia tylko do jego graczy.
Lista stołów (do menu) idzie do wszystkich połączonych.
"""
import logging
import threading
from typing import Callable, Optional

from flask import Flask, request
from flask_socketio import SocketIO, emit, join_room, leave_room

from errors import GameError
from game import Game
from tables import Seat, TableManager

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

manager = TableManager()
# obsługa zdarzeń i sprzątanie w tle zmieniają te same dane; wysyłamy już po zwolnieniu blokady
lock = threading.RLock()
SWEEP_EVERY = 5   # s
_sweeper_started = False


def seat_payload(seat: Seat) -> dict:
    return {"name": seat.name, "token": seat.token, "table": seat.table_id}


def send_tables(lobby: Optional[dict]) -> None:
    if lobby is not None:
        socketio.emit('tables', lobby)


def send_state(table_id: str, state: Optional[dict]) -> None:
    if state is not None:
        socketio.emit('game_state', state, to=table_id)


def sweeper() -> None:
    """Co kilka sekund usuwa porzucone miejsca i stoły."""
    while True:
        socketio.sleep(SWEEP_EVERY)
        with lock:
            changed, list_changed = manager.sweep()
            states = [(t.id, manager.state(t)) for t in changed]
            lobby = manager.lobby_data() if list_changed or changed else None
        for table_id, state in states:
            send_state(table_id, state)
        send_tables(lobby)


def start_sweeper() -> None:
    global _sweeper_started
    with lock:
        if _sweeper_started:
            return
        _sweeper_started = True
    socketio.start_background_task(sweeper)


@socketio.on('connect')
def handle_connect(*_):
    start_sweeper()
    with lock:
        lobby = manager.lobby_data()
    emit('tables', lobby)


@socketio.on('get_tables')
def handle_get_tables(*_):
    with lock:
        lobby = manager.lobby_data()
    emit('tables', lobby)


def sit_down(sit: Callable[[], Seat]) -> None:
    """Wspólna część zakładania stołu i dosiadania się."""
    with lock:
        try:
            seat = sit()
        except GameError as err:
            rejected = err.to_dict()
        else:
            rejected = None
            table = manager.tables[seat.table_id]
            state, lobby = manager.state(table), manager.lobby_data()
    if rejected:
        emit('join_rejected', rejected)
        return
    log.info("%s siada przy stole %s", seat.name, seat.table_id)
    join_room(seat.table_id)
    emit('seated', seat_payload(seat))
    send_state(seat.table_id, state)
    send_tables(lobby)


@socketio.on('create_table')
def handle_create_table(data):
    data = data if isinstance(data, dict) else {}
    sit_down(lambda: manager.create_table(request.sid, data.get('name'), data.get('gods'), data.get('table_name')))


@socketio.on('join_table')
def handle_join_table(data):
    data = data if isinstance(data, dict) else {}
    sit_down(lambda: manager.join_table(request.sid, data.get('table'), data.get('name'), data.get('gods')))


@socketio.on('resume')
def handle_resume(data):
    """Powrót na swoje miejsce po odświeżeniu strony albo zerwanym połączeniu."""
    data = data if isinstance(data, dict) else {}
    with lock:
        try:
            seat, previous = manager.resume(request.sid, data.get('name'), data.get('token'))
        except GameError as err:
            failed = err.to_dict()
        else:
            failed = None
            table = manager.tables[seat.table_id]
            state, lobby = manager.state(table), manager.lobby_data()
    if failed:
        emit('resume_failed', failed)
        return
    if previous:
        # gracz otworzył grę w nowej karcie: stara traci miejsce
        leave_room(seat.table_id, sid=previous)
        socketio.emit('seat_lost', {"code": "seat_taken_over", "params": {}}, to=previous)
    log.info("%s wraca do stołu %s", seat.name, seat.table_id)
    join_room(seat.table_id)
    emit('seated', seat_payload(seat))
    send_state(seat.table_id, state)
    send_tables(lobby)


@socketio.on('leave_table')
def handle_leave_table(*_):
    """Gracz wstaje od stołu. Przeciwnik zostaje i czeka na nowego rywala."""
    with lock:
        seat = manager.seat_of(request.sid)
        if seat is None:
            return
        table_id = seat.table_id
        table, name = manager.leave(request.sid)
        state = manager.state(table) if table else None
        lobby = manager.lobby_data()
    log.info("%s wstaje od stołu %s", name, table_id)
    leave_room(table_id)
    send_state(table_id, state)
    send_tables(lobby)


@socketio.on('disconnect')
def handle_disconnect(*_):
    with lock:
        table = manager.disconnect(request.sid)
        state = manager.state(table) if table else None
        lobby = manager.lobby_data() if table else None
    if table:
        log.info("Rozłączenie przy stole %s", table.id)
        send_state(table.id, state)   # przeciwnik widzi, że gracz jest offline
        send_tables(lobby)            # czekający stół znika z listy, dopóki gracz nie wróci


def run_action(action: Callable[[Game, str], None]) -> None:
    """Ruch w grze przy stole, przy którym siedzi gracz z tego połączenia."""
    with lock:
        found = manager.table_of(request.sid)
        if found is None:
            error, state = GameError("join_first"), None
        else:
            table, name = found
            before = (table.stage, table.game.round)
            try:
                action(table.game, name)
                error = None
            except GameError as err:
                error = err
            state = manager.state(table)
            # lista stołów pokazuje fazę i rundę, więc odświeżamy ją tylko przy ich zmianie
            lobby = manager.lobby_data() if (table.stage, table.game.round) != before else None
    if error:
        # klient dostaje kod i parametry, a tekst wyświetla w języku gracza
        emit('error_message', error.to_dict())
        if state is not None:
            emit('game_state', state)   # przywraca prawdziwy stan po optymistycznej zmianie
        return
    send_state(table.id, state)
    send_tables(lobby)


@socketio.on('confirm_dice')
def handle_confirm_dice(data):
    selected = data.get('selectedIndexes') if isinstance(data, dict) else None
    run_action(lambda game, name: game.confirm_dice(name, selected))


@socketio.on('choose_god')
def handle_choose_god(data):
    data = data if isinstance(data, dict) else {}
    # dodatkowy wybór łaski: ile HP poświęcić (Odyn, Tyr) albo które kości (Frigg, Loki)
    choice = {key: data[key] for key in ('amount', 'targets') if key in data}
    run_action(lambda game, name: game.choose_god(name, data.get('godName'), data.get('level'), choice))


@socketio.on('new_game')
def handle_new_game(*_):
    run_action(lambda game, name: game.rematch())


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
