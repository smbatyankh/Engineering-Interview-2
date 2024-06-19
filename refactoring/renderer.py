
from abc import ABC, abstractmethod
from app import Legend, Protein, Pocket


class Renderer(ABC):
    MOLSTARSUFFIX = '''
                    });
                </script>
            </body>
        </html>
    '''
    
    MOLSTARPREFIX = """asdasdas"""

    @abstractmethod
    def render(self, data_source):
        pass
    
    def save(self, result: str):
        with open("result.html", "w") as e:
            e.write(result)


class LegantRenderer(Renderer):
    
    def render(self, legand: Legend):
        ligand_data = f'var structureData = `{legand.data}`.trim();'
        ligand_type = f'var ligand_type = `{legand.style}`'
        loading = f"loadLigand(viewer, structureData, structureFormat, 'ligand', ligand_type);"

        updated_html = f"{Renderer.MOLSTAR_PREFIX}\n{ligand_data}\n{ligand_type}\n{loading}{Renderer.MOLSTARSUFFIX}"
        
        self.save(updated_html)

class ProteinRenderer(Renderer):
    
    def render(self, protein: Protein):
        protein_data = 'var structureData = `' + protein.data + '`.trim();'
        loading_protein = "loadStructureExplicitly(viewer, structureData, structureFormat, dataLabel='protein', protein_style_type='" + protein.style + "', protein_surface_alpha=" + str(protein.surfac_alpha) + ");"
        
        pocket_surface_msg = 'var pocket_surface_alpha = ' + str(pocket_surface_alpha) + ';'

        loading_pockets = "loadStructureAndPockets(viewer, pocketDataList, pocketFormat, pocket_style_type='" + pocket_style_type + "', pocket_surface_alpha=" + str(pocket_surface_alpha) + ");"
        
        updated_html = Renderer.MOLSTAR_PREFIX + "\n" + protein_data +  "\n"+ loading_protein + "\n"
        for pocket in protein.pockets:
            updated_html = f"{updated_html}{pocket.render()}"
        
        updated_html += "];" + "\n" +  pocket_surface_msg + "\n" + loading_pockets + Renderer.MOLSTARSUFFIX
        self.save(updated_html)

class PocketRenderer(Renderer):
    
    PocketSurfaceColors = {
    'red': ('Red', "0xFF0000"),
    'green': ('Green', "0x008000"),
    'blue': ('Blue', "0x0403FF"),
    'yellow': ('Yellow', "0xFFFF00"),
    'magenta': ('Magenta', "0xFF00FF"),
    'cyan': ('Cyan', "0x00FFFF"),
    'orange': ('Orange', "0xFFA500"),
    'celeste': ('Celeste', "0xb2FFFF"),
    'purple': ('Purple', "0x800080"),
    'brown': ('Brown', "0xA52A2A")
    }
    
    
    def render(self, pocket: Pocket):
        pocket_data = "{ data: `" + pocket + "`.trim(), color: { name: 'uniform', value: '" + PocketSurfaceColors[colors[j]][1] + "' }, label: '" + PocketSurfaceColors[colors[j]][0] + " Pocket' },\n"
        return pocket_data