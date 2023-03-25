from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from StructureFolder import StructureFolder
    from StructureFile import StructureFile

from gdpc.gdpc.interface import placeStructure
from gdpc.gdpc.vector_tools import Box
from glm import ivec3


class Structure:

    connectors: list[dict]
    decorationStructureFiles: dict[str, StructureFile]
    transitionStructureFiles: dict[str, StructureFile]
    structureFile: StructureFile

    position: ivec3 | None

    def __init__(
        self,
        structureFolder: StructureFolder
    ):
        self.structureFile = structureFolder.structureFile
        self.transitionStructureFiles = structureFolder.transitionStructureFiles
        self.decorationStructureFiles = structureFolder.decorationStructureFiles
        self.connectors = []

        self.position = None

    def setPosition(self, position: ivec3 = ivec3(0, 0, 0)):
        self.position = position

    def getBox(self) -> Box:
        if self.position is None:
            self.setPosition()
        # noinspection PyTypeChecker
        return Box(
            self.position,
            ivec3(
                self.structureFile.getSizeX(),
                self.structureFile.getSizeY(),
                self.structureFile.getSizeZ()
            )
        )

    def getPreProcessingSteps(self):
        pass

    def place(
        self,
        position: ivec3 | None = None,
        facing: int = None
    ):
        # TODO create debug structures with different colours of concrete
        if position is not None:
            self.setPosition(position)

        response = placeStructure(
            self.structureFile.file,
            position=self.position, rotate=facing, mirror=None,
            pivot=ivec3(*self.structureFile.getCenterPivot())
        )
        print(f"Placed {self.structureFile.name} ({response}) at {self.position} facing {facing}")

    def getPostProcessingSteps(self):
        pass
