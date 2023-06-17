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


class WideLibrary(Structure):

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

        self.customProperties['archiveCapacity'] = 4

    @property
    def inventoryTable(self) -> dict[str, (float, int)]:
        return {
            'map': (0.2, 1),
            'writable_book': (0.4, 1),
            'written_book': (0.97, 1),
            'book': (0.4, 1),
            'paper': (0.1, 16),
            'music_disc_13': (0.001, 1),
            'music_disc_blocks': (0.001, 1),
            'music_disc_cat': (0.001, 1),
            'music_disc_chirp': (0.001, 1),
            'music_disc_far': (0.001, 1),
            'music_disc_mall': (0.001, 1),
            'music_disc_pigstep': (0.001, 1),
            'music_disc_5': (0.0001, 1),
            'disc_fragment_5': (0.004, 1),
            'music_disk_ward': (0.001, 1),
            'music_disk_11': (0.001, 1),
            'echo_shard': (0.001, 1),
            'name_tag': (0.08, 1),
            'golden_apple': (0.0009, 1),
        }

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

        # Libraries are expensive
        cost += 8

        return cost

    def doPostProcessingSteps(self, node: Node = None):
        super().doPostProcessingSteps(node)

        # TODO fill chest with random paper, books, maps

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
