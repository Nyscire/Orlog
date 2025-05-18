class God:
    def __init__(self,name,description,levels_description) -> None:
        self.name=name 
        self.description=description
        self.levels_description=levels_description
        self.level=None


    def return_data(self):
        data = {"name":self.name,
                "description":self.description,
                "levels":self.levels_description,
                "level":self.level}
        
        return data