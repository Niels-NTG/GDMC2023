from pathlib import Path
from typing import Optional

from glm import ivec3

import globals
from StructureBase import Structure as StructureBase
from Connector import Connector


class NarrowShortBridge(StructureBase):

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
                    'narrow_hub',
                    'narrow_hallway',
                    'narrow_exit',
                    'narrow_bridge_arch_start'
                ]
            ),
            Connector(
                facing=2,
                nextStructure=[
                    'narrow_hub',
                    'narrow_hallway',
                    'narrow_exit',
                    'narrow_bridge_arch_start'
                ]
            )
        ]
