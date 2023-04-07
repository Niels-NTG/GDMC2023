from __future__ import annotations

import numpy as np
from glm import ivec3
from numpy.random import Generator

import globals
from StructureFolder import StructureFolder
from gdpc.gdpc.vector_tools import Box
import vectorTools
import worldTools
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
        self.facing = self.rng.integers(4) if facing is None else facing
        self.candidateStructures = candidateStructures

        self.selectedStructure, self.score = self.selectStructure()

        globals.structureCount = globals.structureCount + 1
        self.place()
        self.createChildNodes()

    def selectStructure(self) -> tuple[Structure | None, int]:
        if self.parentNode is None:

            startPosition = ivec3(
                globals.buildarea.offset.x + self.rng.choice(globals.buildarea.size.x),
                0,
                globals.buildarea.offset.y + self.rng.choice(globals.buildarea.size.y)
            )
            startPosition.y = worldTools.getHeightAt(startPosition)
            # TODO add a list of structures that could be used for the starting node
            startStructure = NarrowHub(
                position=startPosition,
                facing=self.facing
            )

            startStructureScore = self.evaluateCandidateStructure(startStructure)
            if startStructureScore > 0:
                return startStructure, startStructureScore
            # If starting location is not suitable, attempt to find another starting location.
            return self.selectStructure()

        if len(self.candidateStructures) > 0:

            # Pick random candidateStructure, remove from pool when picked
            candidateStructureIndex = self.rng.choice(len(self.candidateStructures))
            structureName = self.candidateStructures.pop(candidateStructureIndex)

            if structureName in globals.structureFolders:
                structureFolder: StructureFolder = globals.structureFolders[structureName]
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
                    return selectedStructure, candidateScore
                # If score is zero, find another candidate structure
                return self.selectStructure()

        return None, 0

    def evaluateCandidateStructure(self, candidateStructure: Structure = None):
        if candidateStructure is None:
            return 0

        # DEBUG Return 0 if there are too many structures.
        if globals.structureCount > globals.maxStructureCount:
            return 0

        # Return 0 if structure is outside the build area.
        if worldTools.isStructureInsideBuildArea(candidateStructure) is False:
            return 0

        # Return 0 if structure intersects with existing structure.
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
        
    def createChildNodes(self):
        if self.selectedStructure:
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

    def place(self):
        if self.selectedStructure:
            self.selectedStructure.place()
            globals.nodeList.append(self)

    def __repr__(self):
        return f'{__class__.__name__} {self.selectedStructure}'
