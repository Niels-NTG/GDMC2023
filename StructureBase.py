from __future__ import annotations

import functools
from typing import TYPE_CHECKING

import globals
import worldTools

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

    preProcessingSteps: list[worldTools.PlacementInstruction]

    _position: ivec3
    _facing: int

    def __init__(
        self,
        structureFolder: StructureFolder,
        position: ivec3,
        facing: int = 0,
    ):

        self.structureFile = structureFolder.structureFile
        self.transitionStructureFiles = structureFolder.transitionStructureFiles
        self.decorationStructureFiles = structureFolder.decorationStructureFiles
        self.connectors = []

        self.preProcessingSteps = []

        self.position = position
        self.facing = facing

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
        cost = 1.0

        # TODO self.preProcessingSteps = [] may need to be reset when structure is being evaluated
        cost += worldTools.calculateTreeCuttingCost(self.rectInWorldSpace) * 0.2

        return cost

    def doPreProcessingSteps(self):
        self.preProcessingSteps.extend(worldTools.getTreeCuttingInstructions(self.rectInWorldSpace))
        for preProcessingStep in self.preProcessingSteps:
            globals.editor.placeBlockGlobal(
                position=preProcessingStep.position,
                block=preProcessingStep.block,
            )

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
