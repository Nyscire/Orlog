from flask import Flask, request
from flask_socketio import SocketIO, emit, join_room
from Game import Game

# Inicjalizacja aplikacji
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

class AppController:
    def __init__(self):
        self.games = {}  # room_id -> Game instance

    def create_or_get_game(self, room_id):
        if room_id not in self.games:
            self.games[room_id] = Game(room_id)
        return self.games[room_id]

    def add_player_to_game(self, room_id, sid):
        game = self.create_or_get_game(room_id)
        success = game.add_player(sid)
        return success, game

# Globalny kontroler gry
controller = AppController()

@socketio.on('join_game')
def on_join(data):
    room_id = data['room']
    sid = request.sid
    success, game = controller.add_player_to_game(room_id, sid)
    print(f"[JOIN] SID: {sid} joined room {room_id}, success: {success}")
    print(f"[DEBUG] Player count: {len(game.players)}, current_turn: {game.current_turn}")
    if success:
        join_room(room_id)
        emit('game_update', game.to_dict(), room=room_id)
    else:
        emit('error', {'message': 'Game is full or player already joined.'})


@socketio.on('roll_dice')
def on_roll(data):
    room_id = data['room']
    sid = request.sid
    game = controller.create_or_get_game(room_id)
    result = game.roll_dice_for_player(sid)
    if result:
        emit('dice_result', result, room=room_id)
        emit('game_update', game.to_dict(), room=room_id)  # <== TO JEST KLUCZOWE
    else:
        emit('error', {'message': 'Invalid player or room.'})


@socketio.on('attack')
def on_attack(data):
    room_id = data['room']
    sid = request.sid
    game = controller.create_or_get_game(room_id)
    if game.perform_attack(sid):
        emit('game_update', game.to_dict(), room=room_id)
    else:
        emit('error', {'message': 'Attack failed or not your turn.'})

@socketio.on('drain_mana')
def on_drain_mana(data):
    room_id = data['room']
    sid = request.sid
    game = controller.create_or_get_game(room_id)
    if game.drain_mana(sid):
        emit('game_update', game.to_dict(), room=room_id)
    else:
        emit('error', {'message': 'Mana drain failed or not your turn.'})

# Uruchomienie serwera
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)
