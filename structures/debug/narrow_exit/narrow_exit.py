from pathlib import Path
import globals
from StructureBase import Structure as StructureBase


class NarrowExit(StructureBase):

    def __init__(self):
        super().__init__(structureFolder=globals.structureFolders[Path(__file__).parent.name])
        self.connectors = [
            {
                'facing': 2,
                'nextStructure': [
                    'narrow_hub',
                    'narrow_hallway',
                    'narrow_short_bridge'
                ]
            }
        ]
