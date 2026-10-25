import logging
from typing import Callable, Dict, Optional

from flask import Flask, request
from flask_socketio import SocketIO, emit

from game import Game, GameError

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

game = Game()
# Mapa socket ID → nazwa gracza. Tylko powiązany socket może wykonywać ruchy danego gracza.
sid_to_player: Dict[str, str] = {}


def reset_server() -> None:
    global game
    game = Game()
    sid_to_player.clear()


def is_connected(name: str) -> bool:
    return name in sid_to_player.values()


def state_payload() -> dict:
    """Stan gry plus informacja, którzy gracze są teraz połączeni."""
    data = game.return_data()
    for player in data["players"]:
        player["connected"] = is_connected(player["name"])
    return data


def broadcast_state() -> None:
    socketio.emit('game_state', state_payload())
    socketio.emit('lobby', game.lobby_data())


def send_error(message: str) -> None:
    emit('error_message', message)
    # Przywraca prawdziwy stan po optymistycznej zmianie w interfejsie
    emit('game_state', state_payload())


def run_action(action: Callable[[str], None]) -> None:
    name: Optional[str] = sid_to_player.get(request.sid)
    if name is None or name not in game.players:
        send_error("Najpierw dołącz do gry.")
        return
    try:
        action(name)
    except GameError as err:
        send_error(str(err))
        return
    broadcast_state()


@socketio.on('connect')
def handle_connect(*_):
    emit('lobby', game.lobby_data())


@socketio.on('get_lobby')
def handle_get_lobby(*_):
    emit('lobby', game.lobby_data())


@socketio.on('submit_player_name')
def handle_submit_player_name(data):
    # z menu przychodzi {"name": ..., "gods": [...]}; sama nazwa też działa
    if isinstance(data, dict):
        name, god_names = data.get('name'), data.get('gods')
    else:
        name, god_names = data, None
    if not isinstance(name, str) or not name.strip():
        emit('join_rejected', 'Podaj nazwę gracza.')
        return
    name = name.strip()

    bound_name = sid_to_player.get(request.sid)
    if bound_name is not None and bound_name != name:
        emit('join_rejected', f'Grasz już jako {bound_name}.')
        return

    # Powrót gracza po odświeżeniu strony lub zerwanym połączeniu
    if name in game.players:
        if is_connected(name) and bound_name != name:
            emit('join_rejected', 'Ta nazwa jest już zajęta.')
            return
        sid_to_player[request.sid] = name
        log.info("Gracz wrócił do gry: %s", name)
        broadcast_state()  # drugi gracz od razu widzi, że przeciwnik wrócił
        return

    # Porzucona gra (żaden z jej graczy nie jest połączony) ustępuje miejsca nowej
    if game.is_full and not any(is_connected(n) for n in game.players):
        log.info("Poprzednia gra porzucona, zaczynamy nową")
        reset_server()

    try:
        game.register_player(name, god_names)
    except GameError as err:
        emit('join_rejected', str(err))
        return
    sid_to_player[request.sid] = name
    log.info("Gracz dołączył: %s", name)

    if game.can_start:
        game.start()
        log.info("Wszyscy gracze gotowi — startujemy grę!")
    broadcast_state()


@socketio.on('disconnect')
def handle_disconnect(*_):
    name = sid_to_player.pop(request.sid, None)
    if name is None:
        return
    log.info("Gracz rozłączony: %s", name)
    if is_connected(name) or name not in game.players:
        return
    # W lobby zwalniamy miejsce, żeby nowa osoba nie czekała na kogoś, kto wyszedł.
    # W trakcie gry miejsce zostaje, a przeciwnik dostaje informację, że gracz jest offline.
    game.remove_waiting_player(name)
    broadcast_state()


@socketio.on('leave_lobby')
def handle_leave_lobby(*_):
    name = sid_to_player.get(request.sid)
    if name is not None and game.remove_waiting_player(name):
        sid_to_player.pop(request.sid, None)
        log.info("Gracz wyszedł z lobby: %s", name)
        broadcast_state()


@socketio.on('leave_game')
def handle_leave_game(*_):
    """Gracz kończy partię: obaj wracają do menu, a serwer jest wolny na nową grę."""
    name = sid_to_player.get(request.sid)
    if name is None or name not in game.players:
        return
    if game.stage == "waiting":
        handle_leave_lobby()
        return
    log.info("Gracz zakończył partię: %s", name)
    others = [sid for sid, player in sid_to_player.items() if player != name]
    for sid in others:
        socketio.emit('game_ended', f'{name} kończy partię. Możesz zacząć nową grę.', to=sid)
    reset_server()
    broadcast_state()


@socketio.on('confirm_dice')
def handle_confirm_dice(data):
    selected = data.get('selectedIndexes') if isinstance(data, dict) else None
    run_action(lambda name: game.confirm_dice(name, selected))


@socketio.on('choose_god')
def handle_choose_god(data):
    data = data if isinstance(data, dict) else {}
    run_action(lambda name: game.choose_god(name, data.get('godName'), data.get('level')))


@socketio.on('new_game')
def handle_new_game(*_):
    run_action(lambda name: game.rematch())


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
