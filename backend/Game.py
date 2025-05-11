import random
from player import Player
from typing import Dict,List
class Game:
    DICES=["axe", "arrow", "helmet", "shield", "mana_drain"]

    def __init__(self,player1:Player,player2:Player):
        self.player1=player1
        self.player2=player2
        self.current_move=player1
        self.round=1
        self.turn = 1
        self.winner=False
        self.stage="RZUT"



    def play_game(self,name:str,):
        pass

    def change_current_player(self):
        if self.current_move==self.player1:
            self.current_move=self.player2
        else:
            self.current_move = self.player2

        
        

        
        
        
        
        
        self.round+=1

