class Ligand:
    
    def __init__(self, path: str, style: str):
        self.path = path
        self.style = style
        self.get_data()
        
    def get_data(self):
        with open(self.path, 'r') as f:
            self.data = f.read()
            self.data = self.data.replace('\n', '\\n')
