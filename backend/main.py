from flask import Flask
from flask_socketio import SocketIO, emit
from game import Game
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")  # Umożliwia CORS dla frontendów na innych portach

@socketio.on('connect')
def handle_connect():
    print('Nowe połączenie z klientem')
    emit('game_state', {'state': 'initial'})  # Przykładowe dane stanu gry

@socketio.on('player_action')
def handle_player_action(data):
    print(f'Otrzymano akcję gracza: {data}')
    # Przetwarzanie akcji gracza i aktualizacja stanu gry
    emit('game_state', {'state': 'updated'}, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
