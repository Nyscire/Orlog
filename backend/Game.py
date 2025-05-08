import random
from player import Player

class Game:
    def __init__(self, room_id):
        self.room_id = room_id
        self.players = []  # lista Player
        self.current_turn = None
        self.dice_faces = ["axe", "arrow", "helmet", "shield", "mana_drain"]

    def add_player(self, sid):
        if any(p.sid == sid for p in self.players):
            return False  # gracz już dołączony
        if len(self.players) >= 2:
            return False  # gra pełna

        player = Player(sid)
        self.players.append(player)

        if len(self.players) == 2 and self.current_turn is None:
            self.current_turn = self.players[0].sid  # pierwszy gracz zaczyna
        return True

    def get_player_by_sid(self, sid):
        for player in self.players:
            if player.sid == sid:
                return player
        return None

    def get_opponent(self, sid):
        for player in self.players:
            if player.sid != sid:
                return player
        return None

    def roll_dice_for_player(self, sid):
        if self.current_turn != sid:
            print(f"[ROLL] Not {sid}'s turn.")
            return None

        player = self.get_player_by_sid(sid)
        if not player:
            return None

        player.reset_temporary_stats()
        dice_faces = ["axe", "arrow", "helmet", "shield", "mana_drain"]
        results = [random.choice(dice_faces) for _ in range(6)]

        for face in results:
            player.add_temporary_stat(face)
        player.has_rolled_dice = True
        print(f"[ROLL] Player {sid} rolled: {results}")
        return {"sid": sid, "results": results}


    def perform_attack(self, sid):
        if self.current_turn != sid:
            return False

        attacker = self.get_player_by_sid(sid)
        defender = self.get_opponent(sid)

        if not attacker or not defender:
            return False

        if not attacker.has_rolled_dice:
            return False  # nie można atakować bez rzutu

        # Oblicz i zadaj obrażenia
        damage = attacker.calculate_attack_damage(defender)
        defender.hp = max(0, defender.hp - damage)

        # Wysysanie many
        if attacker.temp_stats["mana_drain"] > 0:
            if attacker.mana > defender.mana:
                transfer = min(attacker.temp_stats["mana_drain"], defender.mana)
                attacker.mana += transfer
                defender.mana -= transfer

        attacker.has_rolled_dice = False  # zakończona tura
        self.end_turn()
        return True

    def end_turn(self):
        if len(self.players) < 2:
            return

        # Zamiana tury
        if self.current_turn == self.players[0].sid:
            self.current_turn = self.players[1].sid
        else:
            self.current_turn = self.players[0].sid

    def to_dict(self):
        return {
            "room_id": self.room_id,
            "players": [p.to_dict() for p in self.players],
            "current_turn": self.current_turn
        }
