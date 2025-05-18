from player import Player
from god import God
from die import Die
import random
class Game:
    DICES=['axe','arrow','helmet','mana','shield']
    def __init__(self) -> None:
        self.players={}
        self.can_start=False
        self.round = 1
        self.turn=1
        self.winner= None
        self.current_move=None
        self.stage=None

    def register_player(self,player_name:str):
        loki=God("loki","Zadaj obrażenia zależne od poziomu",{1:"2 obrazen",2:"5 obrażeń",3:"6 obrazen"})
        self.players[player_name]=Player(player_name,[loki])
        if len(self.players)==2:
            self.can_start=True
            self.current_move=next(iter(self.players))
            self.stage="gods"


    def roll_dice(self,player):
        for _ in range(6):
            stat = random.choice(self.DICES)
            mana=random.choice([True,False])
            player.rolled_dice.append(Die(stat,mana))

    def start(self):
        print("AKTUALNY RUCH:",self.players[self.current_move])
        self.roll_dice(self.players[self.current_move])
        return self.return_data()
    def return_data(self):
        data={"players":[player.return_data() for player in self.players.values()],
              "current_move":self.current_move,
                "stage":self.stage,
                "winner":self.winner}
        
        return data
    
