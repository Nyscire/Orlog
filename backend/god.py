from __future__ import annotations
from typing import Optional, List, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from player import Player



#TODO Dodać dynamiczne opisy
class God:
    def __init__(self,name,description,levels_description,battle_type,mana_costs) -> None:
        self.name:str=name 
        self.type:str=battle_type
        self.description:str=description
        self.levels_description:List[str]=levels_description
        self.level:Optional[int]=None
        self.mana_costs:List[int]=mana_costs

    def return_data(self) ->Dict[str,str|Dict|None]:
        data = {"name":self.name,
                "description":self.description,
                "levels":self.levels_description,
                "level":self.level}
        
        return data
    
    def activate(self,player:Player):
        pass
    def __str__(self) ->str:
        return f"Name:{self.name}, description:{self.description},levels:{self.levels_description},level:{self.level}"


class Thor(God):
    def activate(self,player:Player):
        values=[3,5,8]
        if self.level:
            player.hp-=values[self.level-1]
        

class Freya(God):
    def activate(self,player:Player):
        values=[2,5,9]
        if self.level:
            player.hp+=values[self.level-1]
        self.level=None

class Heimdall(God):
    def activate(self,player:Player):
        values=[1,2,3]
        if self.level:
            player.temp_stats["axe"]+=values[self.level-1]

        self.level=None

class Loki(God):
    def activate(self,player:Player):
        values=[1,2,3]
        if self.level:
            player.temp_stats["helmet"]+=values[self.level-1]
        self.level=None

def god_factory()->List[God]:
    gods = []
    gods.append(Thor(
        "Thor",
        "Koszt many:3/4/5\nZadaj 3/5/8 obrażeń przeciwnikowi",
        ["3 many:3 obrażeń","4 many:5 obrażeń","many:8 obrażeń"],
        "ofensive",[3/4/5]))
    

    gods.append(Freya(
    "Freya",
    "Koszt many: 2/3/5\nUlecz się o 2/5/9 punkty życia",
    ["2 many: 2 HP", "3 many: 5 HP", "5 many: 9 HP"],
    "defensive",
    [2, 3, 5]
    ))

    gods.append(Heimdall(
        "Heimdall",
        "Koszt many: 2/3/5\nTymczasowo wzmocnij siłę toporów o 1/2/3 punkty",
        ["2 many: +1 topór", "3 many: +2 topory", "5 many: +3 topór"],
        "ofensive",
        [2, 3, 5]
    ))

    # gods.append(Loki(
    #     "Loki",
    #     "Koszt many: 2/3/5\nTymczasowo wzmocnij siłę tarczy o 1/2/3 punkty",
    #     ["2 many: +1 tarcza", "3 many: +2 tarcze", "5 many: +3 tarcze"],
    #     "defensive",
    #     [2, 3, 5]
    # ))



    return gods