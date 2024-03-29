from __future__ import annotations

from copy import deepcopy
from typing import Callable, Any

import numpy as np
from glm import ivec3

import globals
from Connector import Connector
from StructureBase import Structure
import worldTools
import vectorTools


class Node:

    structure: Structure
    cost: float
    rewardFunction: Callable[[Node], float] | None
    terminationFunction: Callable[[Node], bool] | None
    actionFilter: Callable[[Structure], bool] | None
    settlementType: str | None
    bookKeepingProperties: dict[str, Any]
    bookKeeper: Callable[[Node], None] | None
    rng: np.random.Generator
    parentNode: Node | None
    incomingConnector: Connector | None
    connectorSlots: set[Connector]
    routeNames: set[str]
    possibleActions: set[Action]
    hasPossibleActionsCache: bool

    _bookKeeper: Callable[[Node], None] | None

    def __init__(
        self,
        structure: Structure = None,
        cost: float = 0.0,
        parentNode: Node | None = None,
        parentConnector: Connector | None = None,
        rewardFunction: Callable[[Node], float] = None,
        terminationFunction: Callable[[Node], bool] = None,
        actionFilter: Callable[[Structure], bool] = None,
        settlementType: str = None,
        bookKeepingProperties: dict[str, Any] = None,
        bookKeeper: Callable[[Node], None] = None,
        rng: np.random.Generator = np.random.default_rng(),
    ):
        self.structure = structure
        self.cost = cost
        self.rewardFunction = rewardFunction
        self.terminationFunction = terminationFunction
        self.actionFilter = actionFilter
        self.settlementType = settlementType
        self.bookKeepingProperties = deepcopy(bookKeepingProperties if bookKeepingProperties else dict())

        self.bookKeeper = bookKeeper

        self.rng = rng

        self.parentNode = parentNode
        self.incomingConnector = None
        self.connectorSlots = set()
        if parentConnector:
            self.incomingConnector = parentConnector
            rearFacingConnector = structure.rearFacingConnector
            rearFacingConnector.finalNode = parentNode
            self.connectorSlots.add(rearFacingConnector)

        self.routeNames = set()

        self.possibleActions = set()
        self.hasPossibleActionsCache = False

    @property
    def bookKeeper(self):
        return self._bookKeeper

    @bookKeeper.setter
    def bookKeeper(self, bookKeeper: Callable[[Node], None]):
        if bookKeeper is None:
            self._bookKeeper = None
        else:
            self._bookKeeper = bookKeeper
            bookKeeper(self)

    def finalize(self, nextNode: Node = None, routeName: str = None, clearActionCache: bool = False):
        if clearActionCache:
            self.possibleActions.clear()
            self.hasPossibleActionsCache = False
        elif self.hasPossibleActionsCache and nextNode:
            for possibleAction in self.possibleActions.copy():
                if possibleAction.connector == nextNode.incomingConnector:
                    self.possibleActions.remove(possibleAction)
        if nextNode:
            nextNode.incomingConnector.finalNode = nextNode
            self.connectorSlots.add(nextNode.incomingConnector)
        if routeName:
            self.routeNames.add(routeName)
        globals.nodeList.add(self)

    def doPreProcessingSteps(self):
        self.structure.doPreProcessingSteps(self)

    def place(self):
        self.structure.place()

    def doPostProcessingSteps(self):
        self.structure.doPostProcessingSteps(self)

    @property
    def hasOpenSlot(self) -> bool:
        for connector in self.structure.connectors:
            if connector not in self.connectorSlots:
                return True
        return False

    def evaluateCandidateNextStructure(self, candidateStructure: Structure = None) -> float:
        if self.actionFilter and self.actionFilter(candidateStructure) is False:
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
        return 1

    def getPossibleActions(self) -> list[Action]:
        for connector in self.structure.connectors:
            # Check if slot isn't already occupied by other node
            if connector in self.connectorSlots:
                # Use existing node instead of creating a new one
                matchingConnector = None
                for connectorSlot in self.connectorSlots:
                    if connectorSlot == connector:
                        matchingConnector = connectorSlot
                        break

                if matchingConnector.finalNode and matchingConnector.finalNode != self.parentNode:
                    self.possibleActions.add(Action(
                        existingNode=matchingConnector.finalNode,
                        connector=matchingConnector,
                    ))
                continue
        if self.hasPossibleActionsCache:
            return list(self.possibleActions)
        for connector in self.structure.connectors:

            # Check if slot isn't already occupied by other node
            if connector in self.connectorSlots:
                continue

            connectionRotation: int = (connector.facing + self.structure.facing) % 4

            nextStructures = connector.nextStructure
            for candidateStructureName in nextStructures:
                if candidateStructureName not in globals.structureFolders:
                    print(f'Structure file {candidateStructureName} does not exist')
                    continue
                structureFolder = globals.structureFolders[candidateStructureName]
                # noinspection PyCallingNonCallable
                candidateStructure: Structure = structureFolder.structureClass(
                    facing=connectionRotation,
                    position=ivec3(0, 0, 0),
                    settlementType=self.settlementType,
                )

                nextPosition = vectorTools.getNextPosition(
                    facing=connectionRotation,
                    currentBox=self.structure.box,
                    nextBox=candidateStructure.box,
                    offset=connector.offset,
                ) + self.structure.position
                candidateStructure.position = nextPosition

                candidateStructureCost = self.evaluateCandidateNextStructure(candidateStructure)
                if candidateStructureCost > 0:
                    self.possibleActions.add(Action(
                        structure=candidateStructure,
                        cost=candidateStructureCost,
                        connector=connector,
                    ))
        self.hasPossibleActionsCache = True
        return list(self.possibleActions)

    def takeAction(self, action: Action) -> Node:
        if action.existingNode:
            action.existingNode.cost = action.cost
            action.existingNode.rewardFunction = self.rewardFunction
            action.existingNode.terminationFunction = self.terminationFunction
            # Only invalidate possibleActions cache if a different actionFilter is used
            if action.existingNode.actionFilter != self.actionFilter:
                action.existingNode.actionFilter = self.actionFilter
                action.existingNode.possibleActions = None
            action.existingNode.settlementType = self.settlementType
            return action.existingNode
        return Node(
            structure=action.structure,
            cost=action.cost,
            parentNode=self,
            parentConnector=action.connector,
            rewardFunction=self.rewardFunction,
            terminationFunction=self.terminationFunction,
            actionFilter=self.actionFilter,
            settlementType=self.settlementType,
            bookKeepingProperties=self.bookKeepingProperties,
            bookKeeper=self.bookKeeper,
            rng=self.rng,
        )

    def isTerminal(self) -> bool:
        if self.terminationFunction and self.terminationFunction(self):
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
        return f'{__class__.__name__}; ' \
               f'{self.structure}; ' \
               f'{self.bookKeepingProperties}; {self.rewardFunction(self)}; {self.routeNames}'


class Action:

    structure: Structure
    cost: float
    connector: Connector
    existingNode: Node | None

    def __init__(
        self,
        structure: Structure = None,
        cost: float = 0.0,
        connector: Connector = None,
        existingNode: Node = None,
    ):
        self.connector = connector
        if existingNode:
            self.structure = existingNode.structure
            self.cost = 0
            self.existingNode = existingNode
        else:
            self.structure = structure
            self.cost = cost
            self.existingNode = None

    @property
    def structureFileName(self):
        return self.structure.structureFile.name[:-4]

    def __add__(self, other):
        if isinstance(other, Action):
            return self.cost + other.cost
        return self.cost + other

    def __radd__(self, other):
        return self + other

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __hash__(self):
        return hash((self.connector, self.structureFileName))

    def __repr__(self):
        return f'{__class__.__name__} {self.cost} {self.structure}'
