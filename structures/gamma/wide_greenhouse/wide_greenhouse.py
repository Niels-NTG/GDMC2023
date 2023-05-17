from pathlib import Path
from typing import Optional

from glm import ivec3, ivec2

import globals
import vectorTools
import worldTools
from StructureBase import Structure
from Connector import Connector
from gdpc.gdpc.block import Block


class WideGreenhouse(Structure):

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
            Connector(
                facing=0,
                nextStructure=[
                    'narrow_exit',
                    'narrow_short_bridge',
                ]
            ),
            Connector(
                facing=2,
                nextStructure=[
                    'narrow_exit',
                    'narrow_short_bridge',
                ]
            )
        ]

    def evaluateStructure(self) -> float:
        score = super().evaluateStructure()

        pillarCost = (
            self.position.y - worldTools.getHeightAt(
                pos=self.boxInWorldSpace.middle,
                heightmapType='OCEAN_FLOOR_NO_PLANTS'
            )
        ) * 4 ** 2.0
        if pillarCost < 0:
            # If pillar cost is negative, do not built underground
            return 0.0
        score += pillarCost

        return score

    def doPostProcessingSteps(self):
        super().doPostProcessingSteps()

        # Place pillar
        pillarPositions: list[ivec2] = [
            ivec2(3, 2),
            ivec2(3, 10),
            ivec2(11, 2),
            ivec2(11, 10),
        ]
        for pillarPosition in pillarPositions:
            pillarPosition = vectorTools.rotatePointAroundOrigin2D(
                point=self.position2D + pillarPosition,
                origin=self.rectInWorldSpace.center,
                rotation=self.facing,
            )
            for y in range(
                worldTools.getHeightAt(pos=pillarPosition, heightmapType='OCEAN_FLOOR_NO_PLANTS'),
                self.position.y
            ):
                globals.editor.placeBlockGlobal(
                    position=ivec3(pillarPosition.x, y, pillarPosition.y),
                    block=Block('minecraft:weathered_copper')
                )
