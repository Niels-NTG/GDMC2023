from __future__ import annotations

import numpy as np
from glm import ivec3
from numpy.random import Generator

import globals
from StructureFolder import StructureFolder
from gdpc.gdpc.vector_tools import Box
import vectorTools
from StructureBase import Structure
from structures.debug.narrow_hub.narrow_hub import NarrowHub


class Node:

    candidateStructures: list | None
    facing: int | None
    selectedStructure: Structure
    rng: Generator
    parentNode: Node | None

    def __init__(
        self,
        parentNode: Node = None,
        facing: int = None,
        candidateStructures: list = None,
        rng=np.random.default_rng(),
    ):
        self.rng = rng
        self.parentNode = parentNode
        self.facing = 0 if facing is None else facing
        # self.facing = self.rng.integers(4) if facing is None else facing
        self.candidateStructures = candidateStructures

        self.selectedStructure = self.selectStructure()

        globals.structureCount = globals.structureCount + 1
        if globals.structureCount < globals.maxStructureCount:
            # TODO add Node instances to a tree/graph (NetworkX?) instead of placing it right away
            self.place()

    def selectStructure(self) -> Structure | None:
        if self.parentNode is None:
            # TODO create empty dummy origin structure class that itself finds a suitable initial position in the world
            startStructure = NarrowHub(position=globals.buildarea.offset, facing=self.facing)
            return startStructure
        if len(self.candidateStructures) > 0:
            structureName = self.rng.choice(self.candidateStructures)
            if structureName in globals.structureFolders:
                structureFolder: StructureFolder = globals.structureFolders[structureName]
                if structureFolder is None:
                    raise FileNotFoundError(f'Structure file {structureName} does not exist in global collection.')

                # noinspection PyCallingNonCallable
                selectedStructure: Structure = structureFolder.structureClass(
                    facing=self.facing,
                    position=ivec3(0, 0, 0)
                )

                parentStructureBox: Box = self.parentNode.selectedStructure.box
                selectedStructureBox: Box = selectedStructure.box
                nextPosition = vectorTools.getNextPosition(
                    facing=self.facing,
                    currentBox=parentStructureBox,
                    nextBox=selectedStructureBox
                ) + self.parentNode.selectedStructure.position
                selectedStructure.position = nextPosition

                candidateScore = self.evaluateCandidateStructure(selectedStructure)
                if candidateScore > 0:
                    return selectedStructure
        return None

    def evaluateCandidateStructure(self, candidateStructure: Structure = None):
        if candidateStructure is None:
            return 0

        if len(globals.nodeList) > 1:
            otherNode: Node
            for otherNode in globals.nodeList:
                hasIntersection = candidateStructure.isIntersection(otherNode.selectedStructure)
                if hasIntersection:
                    return 0

        return 1

    @property
    def position(self):
        if self.selectedStructure:
            return self.selectedStructure.position

    def place(self):

        if self.selectedStructure is None:
            return

        self.selectedStructure.place()

        globals.nodeList.append(self)

        for connector in self.selectedStructure.connectors:

            connectionRotation: int = (connector.get('facing') + self.facing) % 4

            if self.parentNode and (connector.get('facing') + self.facing + 2) % 4 == self.facing:
                continue

            # Next node
            Node(
                parentNode=self,
                facing=connectionRotation,
                candidateStructures=connector.get('nextStructure', []),
                rng=self.rng,
            )

    def __repr__(self):
        return f'{__class__.__name__} {self.selectedStructure}'
