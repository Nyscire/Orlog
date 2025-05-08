import random

class Game:
    def __init__(self, room_id):
        self.room_id = room_id
        self.players = {}  # client_id -> {'sid': sid}
        self.current_turn = None
        self.dice = []
        self.hp = {}
        self.mana = {}
        self.round = 1
        self.turn_order = []  # kolejność client_id

    def add_player(self, sid):
        if sid in self.players:
            self.players[sid]['sid'] = sid
        elif len(self.players) < 2:
            self.players[sid] = {'sid': sid}
            self.hp[sid] = 100
            self.mana[sid] = 0
            if len(self.players) == 2:
                self.turn_order = list(self.players.keys())
                self.current_turn = self.turn_order[0]


    def roll_dice(self, client_id):
        if self.current_turn != client_id:
            return []

        self.dice = []
        for _ in range(5):
            self.dice.append({
                'stat_type': random.choice(['arrow', 'axe', 'helmet', 'shield', 'mana'])
            })

        return self.dice

    def attack(self, attacker_id):
        if self.current_turn != attacker_id:
            return

        if len(self.players) < 2:
            return

        # Zakładamy, że dice zostały ustawione wcześniej przez roll_dice
        opponent_id = [pid for pid in self.players if pid != attacker_id][0]

        stats = {'arrow': 0, 'axe': 0, 'mana': 0}
        defense = {'shield': 0, 'helmet': 0}

        for die in self.dice:
            t = die['stat_type']
            if t in stats:
                stats[t] += 1
            elif t in defense:
                defense[t] += 1

        # Atak i obrona
        damage = 0
        if stats['arrow'] > 0:
            damage += max(0, stats['arrow'] - defense['shield'])
        if stats['axe'] > 0:
            damage += max(0, stats['axe'] - defense['helmet'])

        self.hp[opponent_id] = max(0, self.hp[opponent_id] - damage)
        self.mana[attacker_id] += stats['mana']

        self.end_turn()

    def drain_mana(self, client_id):
        if self.current_turn != client_id:
            return

        self.mana[client_id] += 3
        self.end_turn()

    def end_turn(self):
        if len(self.turn_order) < 2:
            return

        # Przechodzimy do kolejnego gracza
        current_index = self.turn_order.index(self.current_turn)
        next_index = (current_index + 1) % 2
        self.current_turn = self.turn_order[next_index]

        if next_index == 0:
            self.round += 1

        self.dice = []  # wyczyść kości na nową turę

    def to_dict(self):
        return {
            'room': self.room_id,
            'players': self.players,
            'current_turn': self.current_turn,
            'dice': self.dice,
            'hp': self.hp,
            'mana': self.mana,
            'round': self.round,
        }
