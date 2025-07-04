from __future__ import annotations

from typing import List,Optional,Dict
from god import God
from die import Die


class Player:
    def __init__(self,name,gods) -> None:
        self.name:int=name 
        self.hp:int=21
        self.mana:int=0
        self.rolled_dice:List[Die]=[]
        self.saved_dice:List[Die]=[]
        self.gods:List[God]=gods
        self.chosen_god:Optional[God]=None
        self.rzuty=3

        

    def choose_dice(self,dice:List[int]) -> None:
        print(f"Wylosowano:{self.rolled_dice}")
        saved_dice = [elem for i, elem in enumerate(self.rolled_dice) if i  in dice]
        self.saved_dice.extend(saved_dice)
        print(f"Zatwierdzono: {saved_dice}")
        self.rolled_dice=[]
        print(f"DEBUG {self.saved_dice=}")
        self.rzuty-=1

    def attack(self,enemy:Player) -> None:
        dmg=0
        my_arrows=self.temp_stats["arrow"]
        my_axes=self.temp_stats["axe"]

        enemy_helmets=enemy.temp_stats["helmet"]
        enemy_shields=enemy.temp_stats["shield"]

        arrow_dmg=my_arrows-enemy_shields
        axe_dmg=my_axes-enemy_helmets
        dmg+=max(arrow_dmg,0)
        dmg+=max(axe_dmg,0)
        print(f"{self.temp_stats=}\n {enemy.temp_stats=}\n {arrow_dmg=}\t {axe_dmg=}\t{dmg=}")
        enemy.hp-=dmg

    @property
    def can_roll(self):
        return self.rzuty>0


    @property
    def temp_stats(self) ->Dict[str,int]:
        stat_summary = {"mana": 0,
                        "arrow":0,
                        "axe":0,
                        "shield":0,
                        "helmet":0}

        for die in self.saved_dice:
            if die.stat not in stat_summary:
                stat_summary[die.stat] = 0
            stat_summary[die.stat] += 1
            if die.gives_mana:
                stat_summary["mana"] += 1
        return stat_summary


    def choose_god(self,god) -> None:
        self.chosen_god=god
        
    def return_data(self) -> Dict[str,str|Dict|None]:
        if self.chosen_god:
            chosen_god_data=self.chosen_god.return_data()
        else:
            chosen_god_data=None
        data={"name":self.name,
              "HP":self.hp,
              "Mana":self.mana,
              "rzuty":self.rzuty,
              "rolled_dice":[die.return_data() for die in self.rolled_dice],
              "saved_dice":[die.return_data() for die in self.saved_dice],
              "gods":[god.return_data() for god in self.gods],
              "chosen_god":chosen_god_data} 
        
        return data
    
    def __str__(self):
        return f"{self.name=}:{self.return_data()}"