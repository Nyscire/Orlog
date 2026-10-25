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


def broadcast_state() -> None:
    socketio.emit('game_state', game.return_data())


def send_error(message: str) -> None:
    emit('error_message', message)
    # Przywraca prawdziwy stan po optymistycznej zmianie w interfejsie
    emit('game_state', game.return_data())


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


@socketio.on('submit_player_name')
def handle_submit_player_name(name):
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
        emit('game_state', game.return_data())
        return

    # Porzucona gra (żaden z jej graczy nie jest połączony) ustępuje miejsca nowej
    if game.is_full and not any(is_connected(n) for n in game.players):
        log.info("Poprzednia gra porzucona, zaczynamy nową")
        reset_server()

    try:
        game.register_player(name)
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
    # W lobby zwalniamy miejsce, żeby nowa osoba nie czekała na kogoś, kto wyszedł
    if game.stage == "waiting" and name in game.players and not is_connected(name):
        del game.players[name]
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
