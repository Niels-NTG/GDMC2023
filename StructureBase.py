from __future__ import annotations

import functools
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from StructureFolder import StructureFolder
    from StructureFile import StructureFile

from glm import ivec3

from Connector import Connector
from gdpc.gdpc.interface import placeStructure
from gdpc.gdpc.vector_tools import Box, Rect


class Structure:

    connectors: list[Connector]
    decorationStructureFiles: dict[str, StructureFile]
    transitionStructureFiles: dict[str, StructureFile]
    structureFile: StructureFile

    _position: ivec3
    _facing: int
    connectorId: int | None

    def __init__(
        self,
        structureFolder: StructureFolder,
        position: ivec3,
        facing: int = 0,
        connectorId: int = None,
    ):

        self.structureFile = structureFolder.structureFile
        self.transitionStructureFiles = structureFolder.transitionStructureFiles
        self.decorationStructureFiles = structureFolder.decorationStructureFiles
        self.connectors = []

        self.position = position
        self.facing = facing
        self.connectorId = connectorId

    @property
    def position(self) -> ivec3:
        return self._position

    @position.setter
    def position(self, value: ivec3):
        self._position = value

    @property
    def facing(self) -> int:
        return self._facing

    @facing.setter
    def facing(self, value: int):
        self._facing = value % 4

    @functools.cached_property
    def box(self) -> Box:
        # noinspection PyTypeChecker
        return Box(
            size=ivec3(
                self.structureFile.sizeX,
                self.structureFile.sizeY,
                self.structureFile.sizeZ
            )
        )

    @property
    def boxInWorldSpace(self) -> Box:
        # noinspection PyTypeChecker
        return Box(
            offset=self.position,
            size=ivec3(
                self.structureFile.sizeX,
                self.structureFile.sizeY,
                self.structureFile.sizeZ
            )
        )

    @functools.cached_property
    def rect(self) -> Rect:
        return self.box.toRect()

    @property
    def rectInWorldSpace(self) -> Rect:
        return self.boxInWorldSpace.toRect()

    def isIntersection(self, otherStructure: Structure = None):
        if otherStructure is None:
            return False
        otherStructureBox = otherStructure.boxInWorldSpace
        otherStructureBox.erode()
        currentBox = self.boxInWorldSpace
        hasIntersection = currentBox.collides(otherStructureBox)
        return hasIntersection

    def isSameType(self, otherStructure: Structure = None):
        if otherStructure:
            return otherStructure.structureFile == self.structureFile
        return False

    def evaluateStructure(self) -> float:
        return 1.0

    def doPreProcessingSteps(self):
        pass

    def place(self):
        self.doPreProcessingSteps()
        # noinspection PyTypeChecker
        response = placeStructure(
            self.structureFile.file,
            position=self.position, rotate=self.facing, mirror=None,
            pivot=self.structureFile.centerPivot
        )
        print(f"Placed {self} ({response}) at {self.position} facing {self.facing}")
        self.doPostProcessingSteps()

    def doPostProcessingSteps(self):
        pass

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __hash__(self):
        return hash((self.structureFile, self.position, self.facing))

    def __repr__(self):
        return f'{__class__.__name__} {self.structureFile} {self.position} {self.facing}'
