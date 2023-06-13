from pathlib import Path
from typing import Optional

from glm import ivec3

import globals
import worldTools
from Connector import Connector
from Node import Node
from StructureBase import Structure
from gdpc.gdpc.block import Block


class NarrowHub(Structure):

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
                    'narrow_short_bridge',
                ],
                transitionStructure=self.transitionStructureFiles['door_east.nbt'],
            ),
            Connector(
                facing=1,
                nextStructure=[
                    'narrow_exit',
                    'narrow_short_bridge',
                ],
                transitionStructure=self.transitionStructureFiles['door_south.nbt'],
            ),
            Connector(
                facing=2,
                nextStructure=[
                    'narrow_exit',
                    'narrow_short_bridge',
                ],
                transitionStructure=self.transitionStructureFiles['door_east.nbt'],
            ),
            Connector(
                facing=3,
                nextStructure=[
                    'narrow_exit',
                    'narrow_short_bridge',
                ],
                transitionStructure=self.transitionStructureFiles['door_south.nbt'],
            )
        ]

    def evaluateStructure(self) -> float:
        cost = super().evaluateStructure()

        pillarCost = (
            self.position.y - worldTools.getHeightAt(
                pos=self.boxInWorldSpace.middle, 
                heightmapType='OCEAN_FLOOR_NO_PLANTS'
            )
        ) ** 2.0
        if pillarCost < 0:
            # If pillar cost is negative, do not built underground
            return 0.0
        cost += pillarCost

        return cost

    def doPostProcessingSteps(self, node: Node = None):
        super().doPostProcessingSteps(node)

        # Place pillar
        pillarPos = self.boxInWorldSpace.middle
        for y in range(
            worldTools.getHeightAt(pos=pillarPos, heightmapType='OCEAN_FLOOR_NO_PLANTS'),
            self.position.y
        ):
            globals.editor.placeBlockGlobal(
                position=ivec3(pillarPos.x, y, pillarPos.z),
                block=Block('minecraft:weathered_copper')
            )
