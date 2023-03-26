from pathlib import Path
import globals
from StructureBase import Structure


class NarrowHub(Structure):

    def __init__(self):
        super().__init__(structureFolder=globals.structureFolders[Path(__file__).parent.name])
        self.connectors = [
            {
                'facing': 0,
                'nextStructure': [
                    'narrow_hallway',
                    'narrow_exit',
                    'narrow_short_bridge'
                ]
            },
            {
                'facing': 1,
                'nextStructure': [
                    'narrow_hallway',
                    'narrow_exit',
                    'narrow_short_bridge'
                ]
            },
            {
                'facing': 2,
                'nextStructure': [
                    'narrow_hallway',
                    'narrow_exit',
                    'narrow_short_bridge'
                ]
            },
            {
                'facing': 3,
                'nextStructure': [
                    'narrow_hallway',
                    'narrow_exit',
                    'narrow_short_bridge'
                ]
            }
        ]