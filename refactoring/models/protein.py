from .pocket import Pocket


class Protein:
    
    def __init__(self, path: str, style: str, surface_alpha: float):
        self.path = path
        self.style = style
        self.surfac_alpha = surface_alpha if not style == "surface" else 1
        self.pockets = []
        self.get_data()
        
    def get_data(self):
        with open(self.path, 'r') as f:
            self.data = f.read()
            self.data = self.data.replace('\n', '\\n')

    def add_pocket(self, pocket: Pocket):
        self.pockets.append(pocket)