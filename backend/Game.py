import random

class Game:
    def __init__(self, room_id):
        self.room = room_id
        self.players = {}  # { sid: { data... } }
        self.hp = {}
        self.mana = {}
        self.dice = []
        self.current_turn = None

    def add_player(self, sid):
        if sid not in self.players and len(self.players) < 2:
            self.players[sid] = {}
            self.hp[sid] = 100
            self.mana[sid] = 0

            # Start gry, jeśli dwóch graczy
            if len(self.players) == 2 and self.current_turn is None:
                self.current_turn = random.choice(list(self.players.keys()))

    def roll_dice(self):
        self.dice = []
        for _ in range(6):
            self.dice.append(self.random_stat_die())

    def random_stat_die(self):
        # Możesz rozszerzyć to o bardziej złożone kości
        stat_types = ['arrow', 'axe', 'helmet', 'shield', 'mana']
        return {'stat_type': random.choice(stat_types)}

    def attack(self, sid):
        if sid != self.current_turn:
            return

        opponent = self.get_opponent(sid)
        if opponent:
            # Prosty przykład obrażeń: 10 za każdą 'axe'
            damage = sum(1 for die in self.dice if die['stat_type'] == 'axe') * 10
            self.hp[opponent] -= damage
            self.hp[opponent] = max(self.hp[opponent], 0)

        self.end_turn()

    def drain_mana(self, sid):
        if sid != self.current_turn:
            return

        mana_gain = sum(1 for die in self.dice if die['stat_type'] == 'mana')
        self.mana[sid] += mana_gain
        self.end_turn()

    def end_turn(self):
        self.dice = []
        sids = list(self.players.keys())
        if len(sids) == 2:
            self.current_turn = sids[1] if self.current_turn == sids[0] else sids[0]

    def get_opponent(self, sid):
        for player_sid in self.players:
            if player_sid != sid:
                return player_sid
        return None

    def to_dict(self):
        return {
            'room': self.room,
            'players': self.players,
            'current_turn': self.current_turn,
            'dice': self.dice,
            'hp': self.hp,
            'mana': self.mana,
        }
