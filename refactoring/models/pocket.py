class Pocket:
    
    def __init__(self, path: str, style: str, surface_alpha: float) -> None:
        self.path = path
        self.style = style
        self.surface_alpha = surface_alpha
        self.color = "red"
        self.get_data()
    
    def get_data(self):
        with open(self.path, 'r') as f:
            self.data = f.read()
            self.data = self.data.replace('\n', '\\n').replace('\t', '\\t')
  