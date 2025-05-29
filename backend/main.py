from flask import Flask
from flask_socketio import SocketIO, emit
from game import Game

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
game = Game(socket=socketio)

# Mapa socket ID → nazwa gracza (opcjonalnie, do dalszego rozwoju)
connected_players = {}

@socketio.on('submit_player_name')
def handle_submit_player_name(name):
    if not name:
        return
    print(f"[INFO] Gracz zgłosił nazwę: {name}")
    game.register_player(name)

    if game.can_start:
        print("[INFO] Wszyscy gracze gotowi — startujemy grę!")
        game.start()
        game_data = game.return_data()
        socketio.emit('game_state', game_data)


@socketio.on('confirm_dice')
def handle_confirm_dice(data):
    player = data['player']
    selected = data['selectedIndexes']
    print(f"[DICE] {player} wybrał kości: {selected}")
    game.update_game_status(selected)
    socketio.emit('game_state', game.return_data())

@socketio.on('choose_god')
def handle_choose_god(data):
    player = data['player']
    god = data['godName']
    level = data['level']
    print(f"[GOD] {player} wybrał: {god} (poziom {level})")
    game.update_game_status(data)
    print("[DEBUG] Gracz: ",game.players[player])
    socketio.emit('game_state', game.return_data())


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
