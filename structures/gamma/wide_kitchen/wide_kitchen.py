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


class WideKitchen(Structure):

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
        self.southEastDoorStructure = self.transitionStructureFiles['south_east_door.nbt']
        self.southWestDoorStructure = self.transitionStructureFiles['south_west_door.nbt']

        self.customProperties['kitchenCapacity'] = 12

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
            ),
            Connector(
                facing=1,
                offset=ivec3(0, 0, 4),
                nextStructure=[
                    'narrow_exit',
                    'narrow_short_bridge_1',
                    'narrow_short_bridge_2',
                    'narrow_short_bridge_3',
                ],
                transitionStructure=self.southWestDoorStructure,
            ),
            Connector(
                facing=1,
                offset=ivec3(0, 0, -4),
                nextStructure=[
                    'narrow_exit',
                    'narrow_short_bridge_1',
                    'narrow_short_bridge_2',
                    'narrow_short_bridge_3',
                ],
                transitionStructure=self.southEastDoorStructure,
            ),
            Connector(
                facing=2,
                nextStructure=[
                    'narrow_exit',
                    'narrow_short_bridge_1',
                    'narrow_short_bridge_2',
                    'narrow_short_bridge_3',
                ]
            ),
            Connector(
                facing=3,
                offset=ivec3(0, 0, 4),
                nextStructure=[
                    'narrow_exit',
                    'narrow_short_bridge_1',
                    'narrow_short_bridge_2',
                    'narrow_short_bridge_3',
                ],
                transitionStructure=self.southWestDoorStructure,
            ),
            Connector(
                facing=3,
                offset=ivec3(0, 0, -4),
                nextStructure=[
                    'narrow_exit',
                    'narrow_short_bridge_1',
                    'narrow_short_bridge_2',
                    'narrow_short_bridge_3',
                ],
                transitionStructure=self.southEastDoorStructure,
            )
        ]

    @property
    def inventoryTable(self) -> dict[str, (float, int)]:
        return {
            'apple': (0.2, 8),
            'mushroom_stew': (0.1, 16),
            'melon_slice': (0.2, 4),
            'carrot': (0.3, 16),
            'potato': (0.3, 16),
            'sweet_berries': (0.1, 16),
            'glow_berries': (0.08, 8),
            'golden_apple': (0.0009, 1),
            'bread': (0.3, 4),
            'cookie': (0.1, 8),
            'beetroot_soup': (0.1, 2),
            'baked_potato': (0.1, 8),
            'poisonous_potato': (0.06, 6),
            'pumpkin_pie': (0.07, 1),
            'beetroot': (0.1, 16),
            'honey_bottle': (0.1, 1),
            'dried_kelp': (0.1, 16),
            'cake': (0.004, 1),
            'water_bucket': (0.04, 1),
            'cocoa_beans': (0.08, 8),
            'pumpkin_seeds': (0.1, 16),
            'brown_mushroom': (0.2, 16),
            'red_mushroom': (0.1, 4),
            'beedroot_seeds': (0.02, 8),
            'wheat_seeds': (0.1, 16),
            'paper': (0.02, 4),
        }

    def evaluateStructure(self) -> float:
        cost = super().evaluateStructure()

        pillarCost = ((
            self.position.y - worldTools.getHeightAt(
                pos=self.boxInWorldSpace.middle,
                heightmapType='OCEAN_FLOOR_NO_PLANTS'
            )
        ) * 4) ** 2.0
        if pillarCost <= 0:
            # If pillar cost is negative, do not built underground
            pillarCost = 4
        cost += pillarCost

        return cost

    def doPostProcessingSteps(self, node: Node = None):
        super().doPostProcessingSteps(node)

        # Place pillar
        pillarPositions: list[ivec2] = [
            ivec2(3, 4),
            ivec2(3, 10),
            ivec2(11, 4),
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
