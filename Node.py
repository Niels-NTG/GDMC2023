from __future__ import annotations

import numpy as np
from glm import ivec3, distance

import globals
from StructureBase import Structure
from gdpc.gdpc.vector_tools import Box
import worldTools
import vectorTools


class Node:

    structure: Structure
    cost: float
    rng: np.random.Generator
    parentNode: Node | None
    connectorSlots: set[int]
    possibleActions: list[Action] | None

    def __init__(
        self,
        structure: Structure = None,
        cost: float = 0.0,
        parentNode: Node | None = None,
        rng: np.random.Generator = np.random.default_rng(),
    ):
        self.structure = structure
        self.cost = cost
        self.parentNode = parentNode
        self.rng = rng

        self.connectorSlots = set()

        self.possibleActions = None

    def finalise(self):
        if self.parentNode and self.structure.connectorId:
            self.parentNode.connectorSlots.add(self.structure.connectorId)
        globals.nodeList.append(self)

    def place(self):
        self.structure.place()

    def hasOpenSlot(self) -> bool:
        for connector in self.structure.connectors:
            if hash(connector) not in self.connectorSlots:
                return True
        return False

    def distanceToGlobalGoal(self) -> float:
        return distance(globals.targetGoldBlockPosition.to_tuple(), self.structure.boxInWorldSpace.middle.to_tuple())

    @staticmethod
    def evaluateCandidateNextStructure(candidateStructure: Structure = None) -> float:
        if candidateStructure is None:
            return 0.0

        if worldTools.isStructureInsideBuildArea(candidateStructure) is False:
            return 0.0

        if worldTools.isStructureTouchingSurface(candidateStructure):
            return 0.0

        for otherNode in globals.nodeList:
            if candidateStructure.isIntersection(otherNode.structure):
                return 0.0

        cost = 0.0

        cost += candidateStructure.evaluateStructure()

        return cost

    @staticmethod
    def getCurrentPlayer() -> int:
        return -1

    def getPossibleActions(self) -> list[Action]:
        if self.possibleActions is not None:
            return self.possibleActions
        possibleActions = []

        for connector in self.structure.connectors:

            # Check if slot isn't alrady occupied by other structure
            connectorId = hash(connector)
            if connectorId in self.connectorSlots:
                continue

            connectionRotation: int = (connector.facing + self.structure.facing) % 4

            # Check if slot for this face isn't occupied by the parent node structure
            if self.parentNode and (connector.facing + self.structure.facing + 2) % 4 == self.structure.facing:
                self.connectorSlots.add(connectorId)
                continue

            connectionOffset = connector.offset

            nextStructures = connector.nextStructure
            self.rng.shuffle(nextStructures)
            for candidateStructureName in nextStructures:
                if candidateStructureName not in globals.structureFolders:
                    continue
                structureFolder = globals.structureFolders[candidateStructureName]
                # noinspection PyCallingNonCallable
                candidateStructure: Structure = structureFolder.structureClass(
                    facing=connectionRotation,
                    position=ivec3(0, 0, 0),
                    connectorId=connectorId
                )

                currentStructureBox: Box = self.structure.box
                candidateStructureBox: Box = candidateStructure.box
                nextPosition = vectorTools.getNextPosition(
                    facing=connectionRotation,
                    currentBox=currentStructureBox,
                    nextBox=candidateStructureBox
                ) + self.structure.position
                candidateStructure.position = nextPosition + connectionOffset

                candidateStructureCost = self.evaluateCandidateNextStructure(candidateStructure)
                if candidateStructureCost > 0:
                    possibleActions.append(Action(
                        structure=candidateStructure,
                        cost=candidateStructureCost,
                    ))

        self.possibleActions = possibleActions
        return possibleActions

    def takeAction(self, action: Action):
        return Node(
            structure=action.structure,
            cost=action.cost,
            parentNode=self,
            rng=self.rng,
        )

    def isTerminal(self) -> bool:
        if self.distanceToGlobalGoal() < 4:
            return True
        if len(self.getPossibleActions()) == 0:
            return True
        return False

    def getReward(self) -> float:
        # only needed for terminal states
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
        cost: float = 0.0,
    ):
        self.structure = structure
        self.cost = cost

    def __add__(self, other):
        if isinstance(other, Action):
            return self.cost + other.cost
        return self.cost + other

    def __radd__(self, other):
        return self + other

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __hash__(self):
        return hash((self.structure, self.cost))

    def __repr__(self):
        return f'{__class__.__name__} {self.cost} {self.structure}'
