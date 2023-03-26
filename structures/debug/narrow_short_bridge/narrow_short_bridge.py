from pathlib import Path
import globals
from StructureBase import Structure as StructureBase


class NarrowShortBridge(StructureBase):

    def __init__(self):
        super().__init__(structureFolder=globals.structureFolders[Path(__file__).parent.name])
        self.connectors = [
            {
                'facing': 0,
                'nextStructure': [
                    'narrow_hub',
                    'narrow_hallway',
                    'narrow_exit',
                    'narrow_bridge_arch_start'
                ]
            },
            {
                'facing': 2,
                'nextStructure': [
                    'narrow_hub',
                    'narrow_hallway',
                    'narrow_exit',
                    'narrow_bridge_arch_start'
                ]
            }
        ]