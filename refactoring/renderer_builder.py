from abc import ABC, abstractmethod
from app import Ligand, Protein, Pocket

class RenderBuilder(ABC):
    MOLSTAR_SUFFIX = '''
                    });
                </script>
            </body>
        </html>
    '''
    
    MOLSTAR_PREFIX = '''
        <html lang="en">
            <head>
                <meta charset="utf-8" />
                <meta name="viewport" content="width=device-width, user-scalable=no, minimum-scale=1.0, maximum-scale=1.0">
                <link rel="icon" href="./favicon.ico" type="image/x-icon">
                <title>Embedded Mol* Viewer</title>
                <style>
                    #app {
                        position: relative;
                        width: 100%;
                        height: 100vh;
                    }
                </style>
                <link rel="stylesheet" type="text/css" href="https://cdn.jsdelivr.net/npm/molstar@latest/build/viewer/molstar.css" />
            </head>
            <body>
                <div id="app"></div>
                <script type="text/javascript" src="https://cdn.jsdelivr.net/npm/molstar@latest/build/viewer/molstar.js"></script>
                <script type="text/javascript">
                    molstar.Viewer.create('app', {
                        layoutIsExpanded: false,
                        layoutShowControls: false,
                        layoutShowRemoteState: false,
                        layoutShowSequence: true,
                        layoutShowLog: false,
                        layoutShowLeftPanel: false,

                        viewportShowExpand: false,
                        viewportShowSelectionMode: true,
                        viewportShowAnimation: true,

                        pdbProvider: 'rcsb',
                        emdbProvider: 'rcsb',
                    }).then(viewer => {
                    viewer.plugin.canvas3d?.setProps({
                        renderer: {
                            backgroundColor: 0xFFFFFF,
                        },
                        camera: {
                            mode: 'orthographic',
                            helper: { axes: { name: 'off', params: {} } },
                        },
                        cameraFog: { name: 'off', params: {} },
                        hiZ: { enabled: true }
                    });

        
        async function loadLigand(viewer, data, format, dataLabel = 'ligand', ligand_type = 'ball-and-stick') {
            const _data = await viewer.plugin.builders.data.rawData({ data: data, label: dataLabel });
            const trajectory = await viewer.plugin.builders.structure.parseTrajectory(_data, format);
            const model = await viewer.plugin.builders.structure.createModel(trajectory);
            const structure = await viewer.plugin.builders.structure.createStructure(model);

            const components = {
                ligand: await viewer.plugin.builders.structure.tryCreateComponentStatic(structure, 'ligand'),
            };

            const builder = viewer.plugin.builders.structure.representation;
            const update = viewer.plugin.build();

            if (components.ligand) {
                builder.buildRepresentation(update, components.ligand, { type: ligand_type }, { tag: 'ligand' });
            }
            
            await update.commit();
        }

        async function loadStructureExplicitly(viewer, data, format, dataLabel = 'protein', style_type = 'cartoon', surface_alpha = 0) {
            const _data = await viewer.plugin.builders.data.rawData({ data: data, label: dataLabel });
            const trajectory = await viewer.plugin.builders.structure.parseTrajectory(_data, format);
            const model = await viewer.plugin.builders.structure.createModel(trajectory);
            const structure = await viewer.plugin.builders.structure.createStructure(model);

            const components = {
                polymer: await viewer.plugin.builders.structure.tryCreateComponentStatic(structure, 'polymer'),
                ligand: await viewer.plugin.builders.structure.tryCreateComponentStatic(structure, 'ligand'),
                water: await viewer.plugin.builders.structure.tryCreateComponentStatic(structure, 'water'),
            };

            const builder = viewer.plugin.builders.structure.representation;
            const update = viewer.plugin.build();
            if (components.polymer) {
                builder.buildRepresentation(update, components.polymer, {
                    type: style_type,
                    typeParams: {
                        alpha: 1,
                        quality: 'high'
                    }
                }, { tag: 'polymer-${style_type}' });

                builder.buildRepresentation(update, components.polymer, {
                    type: 'molecular-surface',
                    typeParams: {
                        alpha: surface_alpha,
                        quality: 'high',
                        smoothness: 1
                    },
                    colorTheme: { name: 'hydrophobicity' }
                }, { tag: 'polymer-surface' });
            }
            if (components.ligand) builder.buildRepresentation(update, components.ligand, { type: 'ball-and-stick' }, { tag: 'ligand' });
            if (components.water) builder.buildRepresentation(update, components.water, { type: 'ball-and-stick', typeParams: { alpha: 0.6 } }, { tag: 'water' });
            
            await update.commit();
        }

        async function loadStructureAndPockets(viewer, pocketDataList, pocketFormat, pocket_style_type='gaussian-surface', pocket_surface_alpha = 1) {
            async function visualizePocket(data, format, color, label) {
                const _data = await viewer.plugin.builders.data.rawData({ data: data, label: label });
                const trajectory = await viewer.plugin.builders.structure.parseTrajectory(_data, format);
                const model = await viewer.plugin.builders.structure.createModel(trajectory);
                const structure = await viewer.plugin.builders.structure.createStructure(model);

                const pocketComponent = await viewer.plugin.builders.structure.tryCreateComponentStatic(structure, 'all');
                if (pocketComponent) {
                    const builder = viewer.plugin.builders.structure.representation;
                    const update = viewer.plugin.build();
                    builder.buildRepresentation(update, pocketComponent, {
                        type: pocket_style_type,
                        typeParams: { alpha: pocket_surface_alpha },
                        color: color.name, colorParams: { value: color.value }
                    }, { tag: label });
                    await update.commit();
                }
            }

            for (let pocket of pocketDataList) {
                await visualizePocket(pocket.data, pocketFormat, pocket.color, pocket.label);
            }
        }

        var pocketFormat = 'pdb'.trim();
        var structureFormat = 'pdb'.trim();
        var ligandFormat = 'pdb'.trim();
    '''

    def __init__(self):
        self._result = ""
    
    def build_prefix(self):
        self._result += RenderBuilder.MOLSTAR_PREFIX
    
    def build_suffix(self):
        self._result += RenderBuilder.MOLSTAR_SUFFIX
    
    def save(self):
        with open("result.html", "w") as e:
            e.write(self._result)

    @abstractmethod
    def build_data(self):
        pass


class LigandRenderBuilder(RenderBuilder):

    def build_data(self, ligand: Ligand):
        ligand_data = f'var structureData = `{ligand.data}`.trim();'
        ligand_type = f'var ligand_type = `{ligand.style}`'
        loading = f"loadLigand(viewer, structureData, structureFormat, 'ligand', ligand_type);"
        self._result += f"\n{ligand_data}\n{ligand_type}\n{loading}"


class ProteinRenderBuilder(RenderBuilder):
    
    def get_loading(self, style: str, surface_alpha: float) -> str:
        return f"loadStructureExplicitly(viewer, structureData, structureFormat, dataLabel='protein',protein_style_type='{style}', protein_surface_alpha='{str(surface_alpha)}');"
        
    def get_loading_pockets(self, style: str, surface_alpha: float) -> str:
        return f"loadStructureAndPockets(viewer, pocketDataList, pocketFormat,pocket_style_type='{style}', pocket_surface_alpha={str(surface_alpha)});"
    
    def build_data(self, protein: Protein):
        protein_data = f'var structureData = `{protein.data}`.trim();'
        self._result += f"\n{protein_data}\n{self.get_loading(protein.style, protein.surfac_alpha)}\n"
        
        if not protein.pockets:
            return 
        
        for pocket in protein.pockets:
            pocket_renderer = PocketRenderer()
            self._result += pocket_renderer.render(pocket)
        first_pocket = protein.pockets[0]
        pocket_surface_msg = f'var pocket_surface_alpha = {first_pocket.surface_alpha};'\
            
        self._result += f"\n{pocket_surface_msg}\n{self.get_loading_pockets(first_pocket.style, first_pocket.surface_alpha)}"
    

class PocketRenderer:
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
        color = PocketRenderer.PocketSurfaceColors[pocket.color]
        pocket_data = (
            "{ data: `" + pocket.data + "`.trim(), "
            "color: { name: 'uniform', value: '" + color[1] + "' }, "
            "label: '" + color[0] + " Pocket' },\n"
        )
        return pocket_data


class Renderer:
    
    def render(self, datasource):
        if isinstance(datasource, Ligand):
            builder = LigandRenderBuilder()
        elif isinstance(datasource, Protein):
            builder = ProteinRenderBuilder()
        
        builder.build_prefix()
        builder.build_data(datasource)
        builder.build_suffix()
        builder.save()
