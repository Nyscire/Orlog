"""Serwer gry: wiele stołów, przy każdym osobna partia dla dwóch graczy.

Każdy stół to pokój Socket.IO, więc stan gry trafia tylko do jego graczy.
Lista stołów (do menu) idzie do wszystkich połączonych.

Konta (opcjonalne) i wyniki partii trzyma baza SQLite (db.py, plik z ORLOG_DB).
Aplikacja wysyła token sesji przy każdym połączeniu (auth Socket.IO), więc po
zerwanym połączeniu gracz od razu jest znowu zalogowany.

Uruchomienie:
  python main.py                                   # u siebie, do grania i testów
  gunicorn -w 1 --threads 200 -b 0.0.0.0:5000 main:app   # na serwerze (zawsze 1 proces,
                                                   # bo stoły są w pamięci)
"""
import logging
import os
import threading
from typing import Callable, Dict, Optional

from flask import Flask, jsonify, request
from flask_socketio import SocketIO, emit, join_room, leave_room

from accounts import Accounts
from db import Database
from errors import GameError
from game import Game
from mailer import Mailer
from stats import Stats
from tables import Seat, TableManager

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

app = Flask(__name__)
# zwykłe wątki + simple-websocket; ten sam tryb w `python main.py` i pod gunicornem
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

db = Database()
accounts = Accounts(db, Mailer())
stats = Stats(db)
manager = TableManager(reserved=accounts.is_registered, recorder=stats.record_match)
# zalogowani na tym serwerze: sid -> {"user": {...}, "token": ...}
logins: Dict[str, dict] = {}
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
    """Co kilka sekund usuwa porzucone miejsca i stoły, a w partiach rankingowych daje walkowery."""
    while True:
        socketio.sleep(SWEEP_EVERY)
        with lock:
            changed, list_changed = manager.sweep()
            states = [(t.id, manager.state(t)) for t in changed]
            updates = rating_updates()
            lobby = manager.lobby_data() if list_changed or changed else None
        for table_id, state in states:
            send_state(table_id, state)
        send_tables(lobby)
        send_accounts(updates)


def start_sweeper() -> None:
    global _sweeper_started
    with lock:
        if _sweeper_started:
            return
        _sweeper_started = True
    socketio.start_background_task(sweeper)


@app.route('/health')
def health():
    """Do sprawdzania, czy serwer żyje (Docker, monitoring, test adresu w aplikacji)."""
    with lock:
        tables, players = len(manager.tables), len(manager.seats)
    return jsonify(status="ok", tables=tables, players=players)


def current_user(sid: Optional[str] = None) -> Optional[dict]:
    entry = logins.get(sid or request.sid)
    return entry["user"] if entry else None


@socketio.on('connect')
def handle_connect(auth=None):
    start_sweeper()
    token = auth.get('token') if isinstance(auth, dict) else None
    user = accounts.session_user(token) if token else None
    with lock:
        if user:
            logins[request.sid] = {"user": user, "token": token}
        lobby = manager.lobby_data()
    # expired: aplikacja miała token, ale sesja wygasła albo hasło zmieniono gdzie indziej
    emit('account', {"user": user, "expired": bool(token and not user)})
    emit('tables', lobby)


# ---------- konta ----------

def sign_in(form: str, action: Callable[[], tuple]) -> None:
    """Wspólna część rejestracji, logowania i resetu hasła: nowa sesja dla tego połączenia."""
    with lock:
        seated = manager.seat_of(request.sid) is not None
    if seated:
        # przy stole gra się pod imieniem, z którym się usiadło
        emit('account_error', {"code": "leave_table_first", "params": {}, "form": form})
        return
    try:
        user, token = action()
    except GameError as err:
        emit('account_error', dict(err.to_dict(), form=form))
        return
    with lock:
        logins[request.sid] = {"user": user, "token": token}
    log.info("%s loguje się (%s)", user["login"], form)
    emit('account', {"user": user, "token": token})


def form_data(data) -> dict:
    return data if isinstance(data, dict) else {}


@socketio.on('register')
def handle_register(data):
    data = form_data(data)
    sign_in('register', lambda: accounts.register(data.get('login'), data.get('email'), data.get('password')))


@socketio.on('login')
def handle_login(data):
    data = form_data(data)
    sign_in('login', lambda: accounts.login(data.get('login'), data.get('password')))


@socketio.on('reset_request')
def handle_reset_request(data):
    data = form_data(data)
    lang = data.get('lang') if data.get('lang') in ('pl', 'en') else 'pl'
    try:
        accounts.request_reset(data.get('login'), lang)
    except GameError as err:
        emit('account_error', dict(err.to_dict(), form='reset'))
        return
    # ta sama odpowiedź, czy konto istnieje, czy nie
    emit('reset_sent', {"login": data.get('login')})


@socketio.on('reset_confirm')
def handle_reset_confirm(data):
    data = form_data(data)
    sign_in('reset', lambda: accounts.confirm_reset(data.get('login'), data.get('code'), data.get('password')))


@socketio.on('logout')
def handle_logout(*_):
    with lock:
        if manager.seat_of(request.sid) is not None:
            seated = True
        else:
            seated = False
            entry = logins.pop(request.sid, None)
    if seated:
        emit('account_error', {"code": "leave_table_first", "params": {}, "form": 'logout'})
        return
    if entry:
        accounts.logout(entry["token"])
    emit('account', {"user": None})


@socketio.on('get_profile')
def handle_get_profile(data):
    """Profil gracza (domyślnie własny): bilans, ranking, bogowie, ostatnie partie."""
    data = form_data(data)
    login = data.get('login') or (current_user() or {}).get('login')
    profile = stats.profile(login)
    if profile is None:
        emit('profile', {"login": login, "missing": True})
        return
    emit('profile', profile)


@socketio.on('get_history')
def handle_get_history(data):
    """Kolejna strona historii partii (przycisk „Więcej”)."""
    data = form_data(data)
    history = stats.history_of(data.get('login'), data.get('before'))
    if history is not None:
        emit('history', history)


@socketio.on('get_ranking')
def handle_get_ranking(*_):
    emit('ranking', {"players": stats.ranking()})


@socketio.on('get_tables')
def handle_get_tables(*_):
    with lock:
        lobby = manager.lobby_data()
    emit('tables', lobby)


def sit_down(sit: Callable[[Optional[dict]], Seat]) -> None:
    """Wspólna część zakładania stołu i dosiadania się."""
    with lock:
        try:
            seat = sit(current_user())
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
    sit_down(lambda user: manager.create_table(request.sid, data.get('name'), data.get('gods'),
                                               data.get('table_name'), bool(data.get('ranked')), user))


@socketio.on('join_table')
def handle_join_table(data):
    data = data if isinstance(data, dict) else {}
    sit_down(lambda user: manager.join_table(request.sid, data.get('table'), data.get('name'), data.get('gods'), user))


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


def rating_updates() -> list:
    """Konta z nowym rankingiem po partii rankingowej, do wysłania po zwolnieniu blokady."""
    changes = manager.pop_rating_changes()
    updates = []
    for sid, entry in logins.items():
        login = entry["user"]["login"]
        if login in changes:
            entry["user"] = dict(entry["user"], rating=changes[login])
            updates.append((sid, entry["user"]))
    return updates


def send_accounts(updates: list) -> None:
    for sid, user in updates:
        socketio.emit('account', {"user": user}, to=sid)


@socketio.on('leave_table')
def handle_leave_table(*_):
    """Gracz wstaje od stołu. Przeciwnik zostaje i czeka na nowego rywala.

    W trwającej partii rankingowej to walkower: przeciwnik wygrywa.
    """
    with lock:
        seat = manager.seat_of(request.sid)
        if seat is None:
            return
        table_id = seat.table_id
        table, name = manager.leave(request.sid)
        updates = rating_updates()
        state = manager.state(table) if table else None
        lobby = manager.lobby_data()
    log.info("%s wstaje od stołu %s", name, table_id)
    leave_room(table_id)
    send_state(table_id, state)
    send_tables(lobby)
    send_accounts(updates)


@socketio.on('disconnect')
def handle_disconnect(*_):
    with lock:
        logins.pop(request.sid, None)
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
            manager.after_action(table)
            updates = rating_updates()
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
    send_accounts(updates)


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
    # serwer wbudowany we Flaska: wygodny u siebie; na serwerze lepiej gunicorn (zob. README)
    socketio.run(app, host=os.environ.get('ORLOG_HOST', '0.0.0.0'),
                 port=int(os.environ.get('ORLOG_PORT', '5000')), allow_unsafe_werkzeug=True)
