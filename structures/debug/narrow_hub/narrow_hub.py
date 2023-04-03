from pathlib import Path
from typing import Optional

from glm import ivec3

import globals
from StructureBase import Structure


class NarrowHub(Structure):

    def __init__(
        self,
        position: Optional[ivec3],
        facing: int = 0,
    ):
        super().__init__(
            structureFolder=globals.structureFolders[Path(__file__).parent.name],
            position=position,
            facing=facing
        )
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
