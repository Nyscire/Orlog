from flask import Flask, request
from flask_socketio import SocketIO, emit, join_room

from Game import Game

app = Flask(__name__)

socketio = SocketIO(app, cors_allowed_origins='*')

games = {}

@socketio.on('connect')
def on_connect():
    print('Client connected:', request.sid)

@socketio.on('disconnect')
def on_disconnect():
    print('Client disconnected:', request.sid)

@socketio.on('join_game')
def on_join(data):
    try:
        room_id = data['room']
    except KeyError:
        emit('error', {'message': 'Room not found in data.'})
        return

    if room_id not in games:
        games[room_id] = Game(room_id)

    game = games[room_id]
    game.add_player(request.sid)
    join_room(room_id)
    emit('game_update', game.to_dict(), room=room_id)

@socketio.on('roll_dice')
def on_roll_dice(data):
    try:
        room_id = data['room']
        sid = data['sid']
    except KeyError:
        emit('error', {'message': 'Missing room or sid in data.'})
        return

    if room_id in games:
        game = games[room_id]
        if game.current_turn == sid:
            game.roll_dice()
            emit('dice_result', game.dice, room=sid)
            emit('game_update', game.to_dict(), room=room_id)
        else:
            emit('error', {'message': 'Not your turn.'}, room=sid)

@socketio.on('attack')
def on_attack(data):
    try:
        room_id = data['room']
        sid = data['sid']
    except KeyError:
        emit('error', {'message': 'Missing room or sid in data.'})
        return

    if room_id in games:
        game = games[room_id]
        game.attack(sid)
        emit('game_update', game.to_dict(), room=room_id)

@socketio.on('drain_mana')
def on_drain_mana(data):
    try:
        room_id = data['room']
        sid = data['sid']
    except KeyError:
        emit('error', {'message': 'Missing room or sid in data.'})
        return

    if room_id in games:
        game = games[room_id]
        game.drain_mana(sid)
        emit('game_update', game.to_dict(), room=room_id)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
