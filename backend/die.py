class Die:
    def __init__(self,stat,mana) -> None:
        self.stat=stat 
        self.gives_mana=mana
    def return_data(self):
        data={"stat":self.stat,
              "gives_mana":self.gives_mana}
        
        return data