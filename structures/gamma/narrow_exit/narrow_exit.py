from pathlib import Path
from typing import Optional

from glm import ivec3

import globals
import vectorTools
import worldTools
from Connector import Connector
from Node import Node
from StructureBase import Structure
from gdpc.gdpc.block import Block


class NarrowExit(Structure):

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
        self.customProperties['exit'] = 1

    @property
    def connectors(self) -> list[Connector]:
        return [
            Connector(
                facing=2,
                nextStructure=[
                    'medium_hub',
                    'narrow_hub',
                    'narrow_short_bridge_1',
                    'narrow_short_bridge_2',
                    'narrow_short_bridge_3',
                    'narrow_stairs_up_1',
                    'narrow_stairs_up_2',
                    'narrow_stairs_down_1',
                    'narrow_stairs_down_2',
                ]
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
        if pillarCost <= 0:
            pillarCost = 2
        cost += pillarCost

        return cost

    def doPostProcessingSteps(self, node: Node = None):
        super().doPostProcessingSteps(node)

        # Place pillar
        pillarPos = self.boxInWorldSpace.middle
        ladderPos = vectorTools.rotatePointAroundOrigin3D(
            origin=pillarPos,
            point=pillarPos + ivec3(1, 0, 0),
            rotation=self.facing
        )
        for y in range(
            worldTools.getHeightAt(pos=pillarPos, heightmapType='OCEAN_FLOOR_NO_PLANTS'),
            self.position.y
        ):
            globals.editor.placeBlockGlobal(
                position=ivec3(pillarPos.x, y, pillarPos.z),
                block=Block('minecraft:weathered_copper')
            )
            globals.editor.placeBlockGlobal(
                position=ivec3(ladderPos.x, y, ladderPos.z),
                block=Block(
                    id='minecraft:ladder',
                    states={'facing': worldTools.facingBlockState(facing=self.facing + 1)}
                )
            )
