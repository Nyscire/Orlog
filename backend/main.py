from flask import Flask, render_template,request
from flask_socketio import SocketIO, emit, join_room

app = Flask(__name__)
socketio = SocketIO(app)

# Przykładowa struktura gry
class Game:
    def __init__(self, room):
        self.room = room
        self.players = {}
        self.current_turn = None
        self.dice = []
        self.hp = {}
        self.mana = {}
        self.round = 1

    def add_player(self, client_id, sid):
        if client_id in self.players:
            self.players[client_id]['sid'] = sid
        elif len(self.players) < 2:
            self.players[client_id] = {'sid': sid}
            self.hp[client_id] = 100
            self.mana[client_id] = 0
            if len(self.players) == 2:
                self.turn_order = list(self.players.keys())
                self.current_turn = self.turn_order[0]

    def roll_dice(self, client_id):
        import random
        # Losowanie kości
        self.dice = [random.randint(1, 6) for _ in range(2)]
        emit('game_update', {'room': self.room, 'players': self.players, 'current_turn': self.current_turn,
                             'dice': self.dice, 'hp': self.hp, 'mana': self.mana, 'round': self.round}, room=self.room)

game = Game('game_room_1')

@socketio.on('join_room')
def on_join(data):
    room = data['room']
    client_id = data['client_id']
    sid = request.sid
    game.add_player(client_id, sid)
    join_room(room)
    emit('game_update', {'room': game.room, 'players': game.players, 'current_turn': game.current_turn,
                         'dice': game.dice, 'hp': game.hp, 'mana': game.mana, 'round': game.round}, room=room)

@socketio.on('roll_dice')
def on_roll_dice(data):
    room = data['room']
    client_id = data['client_id']
    game.roll_dice(client_id)
    # Aktualizacja gry po rzucie kośćmi
    emit('game_update', {'room': game.room, 'players': game.players, 'current_turn': game.current_turn,
                         'dice': game.dice, 'hp': game.hp, 'mana': game.mana, 'round': game.round}, room=room)

if __name__ == '__main__':
    socketio.run(app, debug=True)
