from __future__ import annotations
from typing import TYPE_CHECKING
from uuid import uuid4

if TYPE_CHECKING:
    from StructureFolder import StructureFolder
    from StructureFile import StructureFile

from glm import ivec3

from gdpc.gdpc.interface import placeStructure
from gdpc.gdpc.vector_tools import Box


class Structure:

    connectors: list[dict]
    decorationStructureFiles: dict[str, StructureFile]
    transitionStructureFiles: dict[str, StructureFile]
    structureFile: StructureFile

    _position: ivec3
    _facing: int

    def __init__(
        self,
        structureFolder: StructureFolder,
        position: ivec3,
        facing: int = 0,
    ):

        self.uuid = uuid4()

        self.structureFile = structureFolder.structureFile
        self.transitionStructureFiles = structureFolder.transitionStructureFiles
        self.decorationStructureFiles = structureFolder.decorationStructureFiles
        self.connectors = []

        self.position = position
        self.facing = facing

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value: ivec3):
        self._position = value

    @property
    def facing(self):
        return self._facing

    @facing.setter
    def facing(self, value: int):
        self._facing = value % 4

    def isSameType(self, otherStructure: Structure = None):
        if otherStructure:
            return otherStructure.structureFile == self.structureFile
        return False

    def getBox(self) -> Box:
        # noinspection PyTypeChecker
        return Box(
            size=ivec3(
                self.structureFile.getSizeX(),
                self.structureFile.getSizeY(),
                self.structureFile.getSizeZ()
            )
        )

    def getPreProcessingSteps(self):
        pass

    def place(self):

        response = placeStructure(
            self.structureFile.file,
            position=self.position, rotate=self.facing, mirror=None,
            pivot=self.structureFile.getCenterPivot()
        )
        print(f"Placed {self} ({response}) at {self.position} facing {self.facing}")

    def getPostProcessingSteps(self):
        pass

    def __repr__(self):
        return f'{__class__.__name__} {self.uuid} {self.structureFile}'
