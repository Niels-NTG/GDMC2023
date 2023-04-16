from pathlib import Path
from typing import Optional

from glm import ivec3

import globals
import vectorTools
import worldTools
from StructureBase import Structure as StructureBase
from gdpc.gdpc.block import Block
from gdpc.gdpc.vector_tools import Box, loop2D


class NarrowBridgeArchStart(StructureBase):

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
                'nextStructure': [
                    'narrow_bridge_middle',
                    'narrow_bridge_arch_end'
                ]
            },
            {
                'facing': 2,
                'nextStructure': [
                    'narrow_short_bridge'
                ]
            }
        ]

    def evaluateStructure(self) -> float:
        score = super().evaluateStructure()

        bridgeStart = self.getPillarBox()
        pillarHeight = self.position.y - worldTools.getHeightAt(pos=bridgeStart.middle, heightmapType='OCEAN_FLOOR')
        if pillarHeight < 0:
            # If pillar cost is negative, do not built underground
            return 0.0
        pillarCost = pow(pillarHeight, 1.22)

        score += pillarCost

        return score

    def doPostProcessingSteps(self):
        super().doPostProcessingSteps()

        # Place pillar
        pillarBox = self.getPillarBox()
        pillarRect = pillarBox.toRect()
        for pillarPosition in loop2D(begin=pillarRect.begin, end=pillarRect.end):
            for y in range(worldTools.getHeightAt(pos=pillarPosition, heightmapType='OCEAN_FLOOR'), self.position.y):
                globals.editor.placeBlockGlobal(
                    position=ivec3(pillarPosition.x, y, pillarPosition.y),
                    block=Block('minecraft:bricks')
                )

    def getPillarBox(self):
        # from x:2, z:1, size 5, 3
        # noinspection PyTypeChecker
        pillarBox = Box(offset=ivec3(2, 0, 1), size=ivec3(3, 0, 5))

        if self.facing > 0:
            offset = vectorTools.rotatePointAroundOrigin(
                point=pillarBox.offset,
                origin=self.structureFile.getCenterPivot(),
                rotation=self.facing
            )
            size = vectorTools.rotatePointAroundOrigin(
                point=pillarBox.end,
                origin=self.structureFile.getCenterPivot(),
                rotation=self.facing
            )
            # noinspection PyTypeChecker
            pillarBox = Box(
                offset=offset,
                size=size - offset
            )

        pillarBox.offset += self.position
        return pillarBox
