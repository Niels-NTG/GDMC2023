from pathlib import Path
from typing import Optional

from glm import ivec3

import globals
from StructureBase import Structure
from Connector import Connector


class NarrowShortBridge2(Structure):

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
        if self.settlementType == 'villageObservationPost':
            return [
                Connector(
                    facing=0,
                    nextStructure=[
                        'medium_hub',
                        'medium_library',
                        'narrow_exit',
                        'narrow_hub',
                        'narrow_stairs_down_1',
                        'narrow_stairs_down_2',
                        'narrow_stairs_up_1',
                        'narrow_stairs_up_2',
                        'wide_beds12',
                        'wide_library',
                        'wide_kitchen',
                        'wide_greenhouse',
                    ]
                ),
                Connector(
                    facing=2,
                    nextStructure=[
                        'medium_hub',
                        'medium_library',
                        'narrow_exit',
                        'narrow_hub',
                        'narrow_stairs_down_1',
                        'narrow_stairs_down_2',
                        'narrow_stairs_up_1',
                        'narrow_stairs_up_2',
                        'wide_beds12',
                        'wide_library',
                        'wide_kitchen',
                        'wide_greenhouse',
                    ]
                )
            ]
        return [
            Connector(
                facing=0,
                nextStructure=[
                    'medium_hallway',
                    'medium_hub',
                    'narrow_exit',
                    'narrow_hub',
                    'narrow_stairs_down_1',
                    'narrow_stairs_down_2',
                    'narrow_stairs_up_1',
                    'narrow_stairs_up_2',
                ]
            ),
            Connector(
                facing=2,
                nextStructure=[
                    'medium_hallway',
                    'medium_hub',
                    'narrow_exit',
                    'narrow_hub',
                    'narrow_stairs_down_1',
                    'narrow_stairs_down_2',
                    'narrow_stairs_up_1',
                    'narrow_stairs_up_2',
                ]
            )
        ]

    def evaluateStructure(self) -> float:
        cost = super().evaluateStructure()

        cost += 3

        return cost