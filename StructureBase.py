from __future__ import annotations

import functools
import string
from typing import TYPE_CHECKING, Any

import vectorTools

if TYPE_CHECKING:
    from StructureFolder import StructureFolder
    from StructureFile import StructureFile
    from Node import Node

from glm import ivec3, ivec2
import numpy as np

import globals
import worldTools
from Connector import Connector
import nbtTools
from gdpc.gdpc.interface import placeStructure
from gdpc.gdpc.vector_tools import Box, Rect, loop3D
from gdpc.gdpc.lookup import INVENTORY_BLOCKS, CONTAINER_BLOCK_TO_INVENTORY_SIZE
from gdpc.gdpc.block_state_tools import rotateFacing
from gdpc.gdpc.minecraft_tools import bookData


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

    @property
    def inventoryTable(self) -> dict[str, (float, int)]:
        return {
            'paper': (0.5, 6),
        }

    def setInventoryBlocks(
        self,
        rng: np.random.Generator = np.random.default_rng()
    ) -> list[worldTools.PlacementInstruction]:
        newInventoryBlockPlacements: list[worldTools.PlacementInstruction] = []
        for pos in loop3D(self.box.size):
            block = nbtTools.getBlockAt(self.structureFile.nbt, pos)
            if block is None:
                continue
            if block.id not in INVENTORY_BLOCKS:
                continue
            inventoryDimensions: ivec2 = CONTAINER_BLOCK_TO_INVENTORY_SIZE[block.id]
            newInventory = []
            for inventorySlots in range(inventoryDimensions.x * inventoryDimensions.y):
                itemType = rng.choice(list(self.inventoryTable.keys()))
                itemRarity, itemMaxQuantity = self.inventoryTable.get(itemType)
                if rng.random() > itemRarity:
                    continue

                newItemDict = {
                    'x': rng.integers(inventoryDimensions.x),
                    'y': rng.integers(inventoryDimensions.y),
                    'material': itemType,
                    'amount': rng.integers(1, itemMaxQuantity + 1),
                }
                if itemType == 'written_book':
                    randomCodes = ''.join(rng.choice(list(string.hexdigits), size=10))
                    randomCodesSampleName = ''.join(rng.choice(list(string.hexdigits), size=8))
                    author = 'The members of the {} research team'.format(rng.choice([
                        'exogeology',
                        'exobiology',
                        'exobiotanica',
                        'exo-ecology',
                        'exo-seismology',
                        'exo-planetary',
                        'exo macro-biology'
                        'exo archaeology'
                    ]))
                    bookText = \
                        'SAMPLE REPORT §4{}§r\n'.format(randomCodes) + \
                        'date: §dSOL{}/EPOC{}:T+{}{}§r\n'.format(
                            rng.integers(1, 9),
                            rng.integers(1, 11),
                            rng.integers(20, 28),
                            rng.integers(0, 61),
                        ) + \
                        author + '§2 PART OF  EXPEDITION {}§r\n'.format(
                            ''.join(rng.choice(list(string.hexdigits), size=3))) + \
                        'SUBJECT: §a SAMPLE OF {}§r\n'.format(randomCodesSampleName) + \
                        '§rINTRODUCTION\n' + \
                        '§k' + ''.join(
                            rng.choice(list(string.hexdigits), size=rng.integers(100, 1000))) + ' §r\f' + \
                        '§rRESULTS and DISCUSSION\n' + \
                        '§k' + ''.join(
                            rng.choice(list(string.hexdigits), size=rng.integers(100, 1000))) + ' §r\f' + \
                        '§rCONCLUSION\n' + \
                        '§k' + ''.join(
                            rng.choice(list(string.hexdigits), size=rng.integers(100, 1000))) + '\f'
                    newItemDict['tag'] = bookData(
                        text=bookText,
                        title='$4 SAMPLE REPORT {}'.format(randomCodes),
                        author=author,
                        description=f'Subject: {randomCodesSampleName}',
                    )
                newInventory.append(newItemDict)
            block = nbtTools.setInventoryContents(block, newInventory)
            transformedPosition = vectorTools.rotatePointAroundOrigin3D(
                origin=self.boxInWorldSpace.middle,
                point=pos + self.boxInWorldSpace.offset,
                rotation=self.facing,
            )
            if block.states.get('facing'):
                block.states['facing'] = rotateFacing(block.states.get('facing'), self.facing)
            newInventoryBlockPlacements.append(worldTools.PlacementInstruction(
                position=transformedPosition,
                block=block,
            ))
        return newInventoryBlockPlacements

    def evaluateStructure(self) -> float:
        cost = 1.0

        cost += worldTools.calculateTreeCuttingCost(self.rectInWorldSpace) * 0.2

        return cost

    def doPreProcessingSteps(self, node: Node = None):
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
        postProcessingSteps: list[worldTools.PlacementInstruction] = []
        postProcessingSteps.extend(self.setInventoryBlocks(node.rng))
        for postProcessingStep in postProcessingSteps:
            globals.editor.placeBlockGlobal(
                position=postProcessingStep.position,
                block=postProcessingStep.block,
            )

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __hash__(self):
        return hash((self.structureFile, self.position, self.facing))

    def __repr__(self):
        return f'{self.structureFile}; pos: {self.position.x},{self.position.y},{self.position.z}; f: {self.facing}'
