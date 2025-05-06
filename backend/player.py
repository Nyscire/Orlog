class Player:
    def __init__(self, sid):
        self.sid = sid
        self.hp = 15
        self.mana = 0
        self.has_rolled_dice = False  # <- DODAJ TO
        self.temp_stats = {
            "axe": 0,
            "arrow": 0,
            "helmet": 0,
            "shield": 0,
            "mana_drain": 0
        }

    def reset_temporary_stats(self):
        for key in self.temp_stats:
            self.temp_stats[key] = 0
        self.has_rolled_dice = False  # <- RESETUJ PRZY KOŃCU TURY

    def add_temporary_stat(self, stat_name):
        if stat_name in self.temp_stats:
            self.temp_stats[stat_name] += 1

    def get_temporary_stats(self):
        return self.temp_stats.copy()

    def calculate_attack_damage(self, opponent):
        melee = max(0, self.temp_stats["axe"] - opponent.temp_stats["helmet"])
        ranged = max(0, self.temp_stats["arrow"] - opponent.temp_stats["shield"])
        return melee + ranged

    def to_dict(self):
        return {
            "sid": self.sid,
            "hp": self.hp,
            "mana": self.mana,
            "temp_stats": self.temp_stats.copy(),
            "has_rolled_dice": self.has_rolled_dice  # <- UDOSTĘPNIJ WE FRONTENDZIE
        }
