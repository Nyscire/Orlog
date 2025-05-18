class Player:
    def __init__(self,name,gods) -> None:
        self.name=name 
        self.hp=21
        self.mana=0
        self.rolled_dice=[]
        self.saved_dice=[]
        self.gods=gods
        self.chosen_god=None
        
    def return_data(self):
        data={"name":self.name,
              "HP":self.hp,
              "Mana":self.mana,
              "rolled_dice":[die.return_data() for die in self.rolled_dice],
              "saved_dice":[die.return_data() for die in self.saved_dice],
              "gods":[god.return_data() for god in self.gods],
              "chosen_god":self.chosen_god}
        
        return data