from pathlib import Path
from typing import Optional

from glm import ivec3

import globals
from StructureBase import Structure
from Connector import Connector


class NarrowShortBridge(Structure):

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
                    # 'medium_hallway',
                    'medium_hub',
                    'narrow_exit',
                    'narrow_hub',
                    'narrow_stairs_down',
                    'narrow_stairs_up_1',
                    'narrow_stairs_up_2',
                    'wide_greenhouse',
                    # 'wide_hub',
                ]
            ),
            Connector(
                facing=2,
                nextStructure=[
                    # 'medium_hallway',
                    'medium_hub',
                    'narrow_exit',
                    'narrow_hub',
                    'narrow_stairs_down',
                    'narrow_stairs_up_1',
                    'narrow_stairs_up_2',
                    'wide_greenhouse',
                    # 'wide_hub',
                ]
            )
        ]
