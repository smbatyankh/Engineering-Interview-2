from typing import Any
from renderer_builder import *
from models import *

if __name__ == '__main__':
    
    # ligand = Ligand("./files/molecules/BEB.pdb", 'ball-and-stick')
    # renderer = Renderer()
    # renderer.render(ligand)
    protein = Protein("./files/proteins/5HOB.pdb", 'cartoon', 0.4)
    pocket_paths = [
            "./files/pockets/5HOB_yellow_pocket.pdb",
            "./files/pockets/5HOB_magenta_pocket.pdb",
            "./files/pockets/5HOB_red_pocket.pdb",
            "./files/pockets/5HOB_blue_pocket.pdb",
            "./files/pockets/5HOB_green_pocket.pdb",
    ]
    for pocket_index, pocket_path in enumerate(pocket_paths):
        protein.add_pocket(
            Pocket(
                pocket_path,
                'gaussian-surface',
                pocket_index
            )
        )

    render = Renderer()
    render.render(protein)