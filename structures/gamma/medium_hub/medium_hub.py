from pathlib import Path
from typing import Optional

from glm import ivec3, ivec2

import globals
import vectorTools
import worldTools
from Connector import Connector
from Node import Node
from StructureBase import Structure
from gdpc.gdpc.block import Block


class MediumHub(Structure):

    def __init__(
        self,
        position: Optional[ivec3],
        facing: int = 0,
        settlementType: str = None,
    ):
        super().__init__(
            structureFolder=globals.structureFolders[Path(__file__).parent.name],
            position=position,
            facing=facing,
            settlementType=settlementType,
        )

    @property
    def connectors(self) -> list[Connector]:
        return [
            Connector(
                facing=0,
                nextStructure=[
                    'narrow_exit',
                    'narrow_short_bridge_1',
                    'narrow_short_bridge_2',
                    'narrow_short_bridge_3',
                ],
                transitionStructure=self.transitionStructureFiles['door.nbt'],
            ),
            Connector(
                facing=1,
                nextStructure=[
                    'narrow_exit',
                    'narrow_short_bridge_1',
                    'narrow_short_bridge_2',
                    'narrow_short_bridge_3',
                ],
                transitionStructure=self.transitionStructureFiles['door.nbt'],
            ),
            Connector(
                facing=2,
                nextStructure=[
                    'narrow_exit',
                    'narrow_short_bridge_1',
                    'narrow_short_bridge_2',
                    'narrow_short_bridge_3',
                ],
                transitionStructure=self.transitionStructureFiles['door.nbt'],
            ),
            Connector(
                facing=3,
                nextStructure=[
                    'narrow_exit',
                    'narrow_short_bridge_1',
                    'narrow_short_bridge_2',
                    'narrow_short_bridge_3',
                ],
                transitionStructure=self.transitionStructureFiles['door.nbt'],
            )
        ]

    def evaluateStructure(self) -> float:
        cost = super().evaluateStructure()

        pillarCost = ((
            self.position.y - worldTools.getHeightAt(
                pos=self.boxInWorldSpace.middle,
                heightmapType='OCEAN_FLOOR_NO_PLANTS'
            )
        ) * 4) ** 2.0
        if pillarCost <= 0:
            pillarCost = 4
        cost += pillarCost

        return cost

    def doPostProcessingSteps(self, node: Node = None):
        super().doPostProcessingSteps(node)

        # Place pillar
        pillarPositions: list[ivec2] = [
            ivec2(4, 4),
            ivec2(6, 4),
            ivec2(4, 6),
            ivec2(6, 6)
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
