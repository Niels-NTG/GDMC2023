from pathlib import Path
from typing import Optional

from glm import ivec3

import globals
from StructureBase import Structure as StructureBase


class NarrowShortBridgeStairsUp(StructureBase):

    def __init__(
        self,
        position: Optional[ivec3],
        facing: int = 0,
    ):

        super().__init__(
            structureFolder=globals.structureFolders[Path(__file__).parent.name],
            position=position,
            facing=facing,
        )
        self.connectors = [
            {
                'facing': 0,
                'offset': ivec3(0, 3, 0),
                'nextStructure': [
                    'narrow_hub',
                    'narrow_hallway',
                    'narrow_exit',
                ]
            },
            {
                'facing': 2,
                'nextStructure': [
                    'narrow_hub',
                    'narrow_hallway',
                    'narrow_exit',
                ]
            }
        ]

    def evaluateStructure(self) -> float:
        cost = super().evaluateStructure()
        cost += 3.0
        return cost
