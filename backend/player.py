class Player:
    def __init__(self, sid):
        self.sid = sid
        self.hp = 100  # Domyślna wartość HP
        self.mana = 0  # Domyślna wartość many
        self.temp_stats = {
            'axe': 0,
            'arrow': 0,
            'shield': 0,
            'helmet': 0
        }

    def to_dict(self):
        """Zwracanie słownika reprezentującego gracza"""
        return {
            "sid": self.sid,
            "hp": self.hp,
            "mana": self.mana,
            "temp_stats": self.temp_stats  # Statystyki tymczasowe
        }

    def calculate_attack_damage(self, opponent):
        """Obliczanie obrażeń ataku"""
        # Przykładowa logika obliczania obrażeń
        return 10  # Wartość obrażeń, może być zależna od różnych czynników
