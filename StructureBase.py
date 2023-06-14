from __future__ import annotations

import functools
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from StructureFolder import StructureFolder
    from StructureFile import StructureFile
    from Node import Node

from glm import ivec3, ivec2

import globals
import worldTools
from Connector import Connector
from gdpc.gdpc.interface import placeStructure
from gdpc.gdpc.vector_tools import Box, Rect


class Structure:

    connectors: list[Connector]
    decorationStructureFiles: dict[str, StructureFile]
    transitionStructureFiles: dict[str, StructureFile]
    structureFile: StructureFile

    settlementType: str | None

    customProperties: dict[str, Any]

    preProcessingSteps: list[worldTools.PlacementInstruction]

    _position: ivec3
    _facing: int

    def __init__(
        self,
        structureFolder: StructureFolder,
        position: ivec3,
        facing: int = 0,
        settlementType: str = None,
    ):

        self.structureFile = structureFolder.structureFile
        self.transitionStructureFiles = structureFolder.transitionStructureFiles
        self.decorationStructureFiles = structureFolder.decorationStructureFiles

        self.settlementType = settlementType

        self.customProperties = dict()

        self.preProcessingSteps = []

        self.position = position
        self.facing = facing

    @property
    def connectors(self) -> list[Connector]:
        return []

    @property
    def position(self) -> ivec3:
        return self._position

    @position.setter
    def position(self, value: ivec3):
        self._position = value

    @property
    def position2D(self) -> ivec2:
        return ivec2(self.position.x, self.position.z)

    @property
    def position2DCentered(self) -> ivec2:
        return self.rectInWorldSpace.center

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

    def isIntersection(self, otherStructure: Structure = None) -> bool:
        if otherStructure is None:
            return False
        otherStructureBox = otherStructure.boxInWorldSpace
        otherStructureBox.erode()
        currentBox = self.boxInWorldSpace
        return currentBox.collides(otherStructureBox)

    def isSameType(self, otherStructure: Structure = None) -> bool:
        if otherStructure:
            return otherStructure.structureFile == self.structureFile
        return False

    @property
    def rearFacingConnector(self) -> Connector:
        for connector in self.connectors:
            if connector.facing == 2:
                return connector
        return Connector(facing=2)

    def evaluateStructure(self) -> float:
        cost = 1.0

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
        # noinspection PyTypeChecker
        placeStructure(
            self.structureFile.file,
            position=self.position, rotate=self.facing, mirror=None,
            pivot=self.structureFile.centerPivot
        )
        print(f'Placed {self}')

    def doPostProcessingSteps(self, node: Node = None):
        for connector in node.connectorSlots:
            if connector.transitionStructure is None:
                continue
            # noinspection PyTypeChecker
            placeStructure(
                connector.transitionStructure.file,
                position=self.position, rotate=(connector.facing + self.facing) % 4, mirror=None,
                pivot=connector.transitionStructure.centerPivot,
            )

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __hash__(self):
        return hash((self.structureFile, self.position, self.facing))

    def __repr__(self):
        return f'{self.structureFile}; pos: {self.position.x},{self.position.y},{self.position.z}; f: {self.facing}'
