from __future__ import annotations

from typing import Callable

import numpy as np
from glm import ivec3

import globals
from Connector import Connector
from StructureBase import Structure
from gdpc.gdpc.vector_tools import Box
import worldTools
import vectorTools


class Node:

    structure: Structure
    cost: float
    rewardFunction: Callable[[Node], float] | None
    rng: np.random.Generator
    incomingConnector: int | None
    connectorSlots: set[int]
    routeNames: set[str]
    possibleActions: list[Action] | None

    def __init__(
        self,
        structure: Structure = None,
        cost: float = 0.0,
        parentConnector: Connector | None = None,
        rewardFunction: Callable[[Node], float] = None,
        rng: np.random.Generator = np.random.default_rng(),
    ):
        self.structure = structure
        self.cost = cost
        self.rewardFunction = rewardFunction
        self.rng = rng

        self.incomingConnector = None
        self.connectorSlots = set()
        if parentConnector:
            self.incomingConnector = hash(parentConnector)
            self.connectorSlots.add(2)

        self.routeNames = set()

        self.possibleActions = None

    def finalise(self, nextNode: Node = None, routeName: str = None):
        if nextNode:
            self.connectorSlots.add(nextNode.incomingConnector)
        if routeName:
            self.routeNames.add(routeName)
        globals.nodeList.append(self)

    def place(self):
        self.structure.place()

    @property
    def hasOpenSlot(self) -> bool:
        for connector in self.structure.connectors:
            if hash(connector) not in self.connectorSlots:
                return True
        return False

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

            # Check if slot isn't already occupied by other structure
            connectorId = hash(connector)
            if connectorId in self.connectorSlots:
                continue

            connectionRotation: int = (connector.facing + self.structure.facing) % 4

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
                        connector=connector,
                    ))

        self.possibleActions = possibleActions
        return possibleActions

    def takeAction(self, action: Action) -> Node:
        return Node(
            structure=action.structure,
            cost=action.cost,
            parentConnector=action.connector,
            rewardFunction=self.rewardFunction,
            rng=self.rng,
        )

    def isTerminal(self) -> bool:
        if self.rewardFunction(self) < 4:
            return True
        if len(self.getPossibleActions()) == 0:
            return True
        return False

    def getReward(self) -> float:
        # only needed for terminal states
        return self.rewardFunction(self)

    def __hash__(self):
        return hash(self.structure)

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __repr__(self):
        return f'{__class__.__name__} {self.routeNames} {self.rewardFunction(self)} {self.structure}'


class Action:

    def __init__(
        self,
        structure: Structure = None,
        cost: float = 0.0,
        connector: Connector = None,
    ):
        self.structure = structure
        self.cost = cost
        self.connector = connector

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
