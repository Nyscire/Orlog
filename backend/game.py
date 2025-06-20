from player import Player
from god import God,god_factory
from die import Die
import random
from typing import Optional,Dict
from copy import deepcopy

class Game:
    DICES=['axe','arrow','helmet','mana','shield']
    GODS=god_factory()
    def __init__(self,socket) -> None:
        self.players:Dict[str,Player]={}
        self.can_start:bool=False
        self.round:int = 1
        self.turn:int=1
        self.winner:Optional[Player] = None
        self.active_player: Optional[str]=None
        self.passive_player: Optional[str]=None
        self.stage: Optional[str]=None
        self.socket = socket


    def find_god(self,god_name) ->God | None:
        for god in self.GODS:
            if god.name==god_name:
                return god

        return None
    
    @property
    def can_players_roll(self) ->bool:
        if self.attacker and self.defender:
            return self.attacker.can_roll or self.defender.can_roll
        return False 

    @property
    def attacker(self) -> Player | None:
        if self.active_player:
            return self.players[self.active_player]
        return None
    
    @property
    def defender(self) -> Player | None:
        if self.passive_player:
            return self.players[self.passive_player]
        return None
    
    def register_player(self,player_name:str) -> None:
        self.players[player_name]=Player(player_name,deepcopy(self.GODS))
        if len(self.players)==2:
            self.can_start=True
            self.active_player,self.passive_player=list(self.players.keys())
            self.stage="dice"


    def roll_dice(self) -> None:
        if self.attacker:
            for _ in range(6-len(self.attacker.saved_dice)):
                stat = random.choice(self.DICES)
                mana=random.choice([True,False])
                self.attacker.rolled_dice.append(Die(stat,mana))
                

    def start(self) ->  None:
        if self.active_player:
            self.roll_dice()
    def reset_stats(self) -> None:
        if self.attacker and self.defender: 
            for player in [self.attacker,self.defender]:
                player.rolled_dice=[]
                player.saved_dice=[]
                player.chosen_god=None
                player.rzuty=3

    
    def activate_gods(self):
        if self.attacker and self.attacker.chosen_god:
            attacker_target=self.defender if self.attacker.chosen_god.type=="ofensive" else self.attacker
            self.attacker.chosen_god.activate(attacker_target) # type: ignore
        if self.defender and self.defender.chosen_god:
            defender_target=self.attacker if self.defender.chosen_god.type=="ofensive" else self.defender
            self.defender.chosen_god.activate(defender_target) # type: ignore
        


    def battle(self) -> None:
        self.grant_mana()
        if self.attacker and self.defender:
            self.activate_gods()
            self.attacker.attack(self.defender)
            if self.defender.hp<=0:
                self.winner=self.attacker
                return
            self.switch_active_player()
            self.attacker.attack(self.defender)
            if self.defender.hp <=0:
                self.winner=self.attacker
                return
            self.reset_stats()
            self.socket.emit('game_state', self.return_data())


    def grant_mana(self) -> None:
        for player in self.players.values():
            player.mana+=player.temp_stats["mana"]

    

    def change_move(self) -> None:
        if self.stage=="dice" and self.turn==1:
            if self.defender and self.defender.rzuty>0:
                self.switch_active_player()
                self.roll_dice()
            elif self.defender and self.defender.rzuty==0 and self.attacker and self.attacker.rzuty==0:
                # Both players done with dice - move to gods stage immediately
                self.switch_active_player()
                self.stage="gods"
                self.turn=1

        elif self.stage=="dice" and self.turn==2:
            self.switch_active_player()
            self.stage="gods"
            self.turn=1

        elif self.stage=="gods" and self.turn==1:
            self.switch_active_player()
            self.turn=2
        else:
            self.battle()
            self.turn=1
            self.switch_active_player()
            self.roll_dice()
            self.stage="dice"

    def update_game_status(self,data) -> None:
        print(f"=== DEBUG update_game_status ===")
        print(f"Active player (attacker): {self.attacker.name if self.attacker else None}")
        print(f"Data received: {data}")
        print(f"Stage: {self.stage}, Turn: {self.turn}")

        if self.attacker:
            if self.stage == "dice":
            # Only process dice selection if player has throws left
                if self.attacker.rzuty > 0:
                    print(f"Before choose_dice - attacker.saved_dice: {self.attacker.saved_dice}")
                    self.attacker.choose_dice(data)
                    print(f"After choose_dice - attacker.saved_dice: {self.attacker.saved_dice}")
                else:
                    print(f"Skipping dice selection - player has no throws left")
                
            else:
                if data:
                    player = data['player']
                    god = data['godName']
                    level = data['level']
                    chosen_god=self.find_god(god)
                    if chosen_god:
                        chosen_god.level=level
                self.attacker.choose_god(chosen_god)
            self.change_move()
        
    def switch_active_player(self) -> None:
        self.active_player,self.passive_player=self.passive_player,self.active_player
    def return_data(self) -> Dict[str,str|Dict|None]:
        data={"players":[player.return_data() for player in self.players.values()],
              "active_player":self.active_player,
                "stage":self.stage,
                "winner":self.winner.name if self.winner else None}
        
        return data
    
