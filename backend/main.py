from flask import Flask, request
from flask_socketio import SocketIO, join_room, emit
import random

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

@app.route("/")
def index():
    return "Orlog Game Backend"

players = {}  # room_id -> list of player_sid

@socketio.on('join_game')
def on_join(data):
    room = data['room']
    join_room(room)
    sid = request.sid

    players.setdefault(room, []).append(sid)
    emit('player_joined', {'sid': sid, 'players': players[room]}, to=room)

@socketio.on('roll_dice')
def on_roll(data):
    room = data['room']
    result = [random.choice(['axe', 'shield', 'arrow']) for _ in range(6)]
    emit('dice_result', {'sid': request.sid, 'dice': result}, to=room)

@socketio.on('use_god_power')
def on_god_power(data):
    room = data['room']
    emit('god_power_used', {
        'sid': request.sid,
        'god': data['god']
    }, to=room)

if __name__ == '__main__':
    run = True
    while run:
        try:
            print("Uruchomiono backend...")
            socketio.run(app, host="0.0.0.0", port=5000)
        except KeyboardInterrupt:
            run= False
            print("Zamknięto poprawnie...")