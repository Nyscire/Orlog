from player import Player
from god import God
from die import Die
import json
class Game:
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
            self.current_move=self.players.keys
            self.stage="dice"
    def return_data(self):
        print(self.players)
        data={"players":[player.return_data() for player in self.players.values()],
              "current_move":self.current_move,
                "stage":self.stage,
                "winner":self.winner}
        
        return data
    
