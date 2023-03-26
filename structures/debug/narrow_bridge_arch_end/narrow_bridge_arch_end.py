from pathlib import Path
import globals
from StructureBase import Structure as StructureBase


class NarrowBridgeArchEnd(StructureBase):

    def __init__(self):
        super().__init__(structureFolder=globals.structureFolders[Path(__file__).parent.name])
        self.connectors = [
            {
                'facing': 0,
                'nextStructure': [
                    'narrow_short_bridge'
                ]
            },
            {
                'facing': 2,
                'nextStructure': [
                    'narrow_bridge_middle',
                    'narrow_bridge_arch_end'
                ]
            }
        ]
