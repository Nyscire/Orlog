import random

class Die:
    STAT_TYPES = ['mana', 'arrow', 'axe', 'helmet', 'shield']

    def __init__(self):
        self.stat_type = None

    def roll(self):
        self.stat_type = random.choice(self.STAT_TYPES)

    def is_mana(self):
        return self.stat_type == 'mana'

    def to_dict(self):
        return {
            'stat_type': self.stat_type
        }
