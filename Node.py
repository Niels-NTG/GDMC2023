from __future__ import annotations
from copy import copy

import numpy as np
from glm import ivec3, distance

import globals
from StructureBase import Structure
from gdpc.gdpc.vector_tools import Box
import worldTools
import vectorTools


class Node:

    structure: Structure
    score: float
    rng: np.random.Generator
    isRoot: bool

    def __init__(
        self,
        structure: Structure = None,
        score: float = 0.0,
        rng: np.random.Generator = np.random.default_rng(),
        isRoot: bool = False
    ):
        self.structure = structure
        self.score = score
        self.rng = rng
        self.isRoot = isRoot

    def place(self):
        self.structure.place()

    def distanceToGlobalGoal(self):
        return distance(globals.targetGoldBlockPosition.to_tuple(), self.structure.boxInWorldSpace.middle.to_tuple())

    @staticmethod
    def evaluateCandidateNextStructure(candidateStructure: Structure = None) -> float:
        if candidateStructure is None:
            return 0.0

        if worldTools.isStructureInsideBuildArea(candidateStructure) is False:
            return 0.0

        # TODO Check if this needs to be adjusted to account for MCTS back prop
        # if len(globals.nodeList) > 1:
        #     otherNode: Node
        #     for otherNode in globals.nodeList:
        #         hasIntersection = candidateStructure.isIntersection(otherNode.structure)
        #         if hasIntersection:
        #             return 0.0

        score = 0.0

        score += candidateStructure.evaluateStructure()

        return score

    @staticmethod
    def getCurrentPlayer():
        return -1

    def getPossibleActions(self) -> list[Action]:
        possibleActions = []

        connectors = copy(self.structure.connectors)
        self.rng.shuffle(connectors)
        for connector in connectors:

            connectionRotation: int = (connector.get('facing') + self.structure.facing) % 4

            # Check if slot for this face isn't occupied by the parent node structure
            if self.isRoot is False and \
                    (connector.get('facing') + self.structure.facing + 2) % 4 == self.structure.facing:
                continue
            # TODO check if slot is not already taken by other nodes

            nextStructures = connector.get('nextStructure', [])
            self.rng.shuffle(nextStructures)
            for candidateStructureName in nextStructures:
                if candidateStructureName not in globals.structureFolders:
                    continue
                structureFolder = globals.structureFolders[candidateStructureName]
                # noinspection PyCallingNonCallable
                candidateStructure: Structure = structureFolder.structureClass(
                    facing=connectionRotation,
                    position=ivec3(0, 0, 0)
                )

                currentStructureBox: Box = self.structure.box
                selectedStructureBox: Box = candidateStructure.box
                nextPosition = vectorTools.getNextPosition(
                    facing=connectionRotation,
                    currentBox=currentStructureBox,
                    nextBox=selectedStructureBox
                ) + self.structure.position
                candidateStructure.position = nextPosition

                candidateStructureScore = self.evaluateCandidateNextStructure(candidateStructure)
                if candidateStructureScore > 0:
                    possibleActions.append(Action(
                        structure=candidateStructure,
                        score=candidateStructureScore,
                    ))

        return possibleActions

    def takeAction(self, action: Action):
        return Node(
            structure=action.structure,
            score=action.score,
            rng=self.rng,
        )

    def isTerminal(self):
        if self.distanceToGlobalGoal() < 10:
            return True
        if len(self.getPossibleActions()) == 0:
            return True
        return False

    def getReward(self):
        # only needed for terminal states
        # return self.score
        # return 0 - self.distanceToGlobalGoal()
        return self.distanceToGlobalGoal()

    def __hash__(self):
        return hash(self.structure)

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __repr__(self):
        return f'{__class__.__name__} {self.distanceToGlobalGoal()} {self.structure}'


class Action:

    def __init__(
        self,
        structure: Structure = None,
        score: float = 0.0,
    ):
        self.structure = structure
        self.score = score

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __hash__(self):
        return hash((self.structure, self.score))

    def __repr__(self):
        return f'{__class__.__name__} {self.score} {self.structure}'
