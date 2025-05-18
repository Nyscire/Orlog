from flask import Flask
from flask_socketio import SocketIO, emit
from game import Game

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
game = Game()

# Mapa socket ID → nazwa gracza (opcjonalnie, do dalszego rozwoju)
connected_players = {}

@socketio.on('submit_player_name')
def handle_submit_player_name(name):
    if not name:
        return
    print(name)
    print(f"[INFO] Gracz zgłosił nazwę: {name}")
    game.register_player(name)

    if game.can_start:
        print("[INFO] Wszyscy gracze gotowi — startujemy grę!")
        game_data = game.start()
        print(game_data)
        socketio.emit('game_state', game_data)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
