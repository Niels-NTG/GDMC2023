from pathlib import Path
import globals
from StructureBase import Structure as StructureBase


class NarrowBridgeMiddle(StructureBase):

    def __init__(self):
        super().__init__(structureFolder=globals.structureFolders[Path(__file__).parent.name])
        self.connectors = [
            {
                'facing': 0,
                'nextStructure': [
                    'narrow_bridge_arch'
                ]
            },
            {
                'facing': 2,
                'nextStructure': [
                    'narrow_bridge_arch'
                ]
            }
        ]
