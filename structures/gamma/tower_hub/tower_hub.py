from pathlib import Path
from typing import Optional

from glm import ivec3, ivec2

import globals
import vectorTools
import worldTools
from StructureBase import Structure
from Connector import Connector
from gdpc.gdpc.block import Block


class TowerHub(Structure):

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
                facing=1,
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
            ),
            Connector(
                facing=3,
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
        ) * 5 ** 2.0
        if pillarCost < 0:
            # If pillar cost is negative, do not built underground
            return 0.0
        score += pillarCost

        return score

    def doPostProcessingSteps(self):
        super().doPostProcessingSteps()

        # Place pillar
        pillarPositions: list[ivec2] = [
            ivec2(6, 3),
            ivec2(3, 6),
            ivec2(10, 3),
            ivec2(13, 6),
            ivec2(6, 13),
            ivec2(3, 10),
            ivec2(10, 13),
            ivec2(13, 10),
            self.rect.size // 2
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
