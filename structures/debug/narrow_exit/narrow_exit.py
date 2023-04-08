from pathlib import Path
from typing import Optional

from glm import ivec3

import globals
import worldTools
from StructureBase import Structure as StructureBase
from gdpc.gdpc.block import Block


class NarrowExit(StructureBase):

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
                'facing': 2,
                'nextStructure': [
                    'narrow_hub',
                    'narrow_hallway',
                    'narrow_short_bridge'
                ]
            }
        ]

    def evaluateStructure(self) -> float:
        score = super().evaluateStructure()

        pillarCost = (
            self.position.y - worldTools.getHeightAt(pos=self.boxInWorldSpace.middle, heightmapType='OCEAN_FLOOR')
        ) ** 2.0
        if pillarCost < 0.0:
            # If pillar cost is negative, do not built underground
            return 0.0
        score += pillarCost

        return score

    def doPostProcessingSteps(self):
        super().doPostProcessingSteps()

        # Place pillar
        pillarPosition = self.boxInWorldSpace.middle
        for y in range(worldTools.getHeightAt(pos=pillarPosition, heightmapType='OCEAN_FLOOR'), self.position.y):
            globals.editor.placeBlockGlobal(
                position=ivec3(pillarPosition.x, y, pillarPosition.z),
                block=Block('minecraft:bricks')
            )
        # TODO place ladder against pillar
