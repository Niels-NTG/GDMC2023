from __future__ import annotations

from typing import Callable

import numpy as np
from glm import ivec3, ivec2

import globals
from Node import Node
from StructureBase import Structure
from gdpc.gdpc import Rect
from structures.gamma.tower_hub.tower_hub import TowerHub
import worldTools
import vectorTools


class RootNode(Node):

    possibleActions: list[Action] | None
    nodeRewardFunction: Callable[[Node], float] | None
    rng: np.random.Generator

    # noinspection PyMissingConstructor
    def __init__(
        self,
        nodeRewardFunction: Callable[[Node], float] = None,
        rng: np.random.Generator = np.random.default_rng(),
    ):
        self.nodeRewardFunction = nodeRewardFunction
        self.rng = rng

        self.structure = TowerHub(
            position=ivec3(0, 0, 0),
            facing=0,
        )

        self.possibleActions = None

        # TODO to improve performance, consider starting an MCTS search for each RootNode instance and then compare
        #   the results to compare the most efficient/cheapest/best one. This can be parralized using Thread library.

    def finalize(self, nextNode: Node = None, routeName: str = None):
        pass

    def doPreProcessingSteps(self):
        pass

    def place(self):
        pass

    def doPostProcessingSteps(self):
        pass

    @property
    def hasOpenSlot(self) -> bool:
        return False

    @staticmethod
    def getCurrentPlayer() -> int:
        return -1

    def getPossibleActions(self) -> list[Action]:
        if self.possibleActions is not None:
            return self.possibleActions
        possibleActions: list[Action] = []

        sampleSize = int(np.sqrt(globals.buildarea.area) // 20)
        sampleLocations = self.rng.uniform(globals.buildarea.begin, globals.buildarea.end, (sampleSize, 2)).astype(int)
        for location in sampleLocations:
            # noinspection PyTypeChecker
            locationRect: Rect = Rect(offset=ivec2(*location), size=self.structure.rect.size)
            if not vectorTools.isRectinRect(globals.buildarea, locationRect):
                continue

            # calculate gradient to find flattest region
            locationEvaluation = worldTools.getSurfaceStandardDeviation(
                rect=locationRect,
                heightmapType='OCEAN_FLOOR_NO_PLANTS'
            )

            if locationEvaluation[0] > 10:
                continue

            candidateStructure = TowerHub(
                position=ivec3(location[0], locationEvaluation[2] + 1, location[1]),
                facing=self.rng.integers(4),
            )
            structureEvaluation = Node.evaluateCandidateNextStructure(candidateStructure)
            if structureEvaluation > 0:
                possibleActions.append(Action(
                    structure=candidateStructure,
                    cost=locationEvaluation[0] + structureEvaluation,
                ))

        self.possibleActions = possibleActions
        return possibleActions

    def takeAction(self, action: Action) -> Node:
        return Node(
            structure=action.structure,
            cost=action.cost,
            rewardFunction=self.nodeRewardFunction,
            rng=self.rng,
        )

    def isTerminal(self) -> bool:
        if len(self.getPossibleActions()) == 0:
            return True
        return False

    def getReward(self) -> float:
        return 1.0

    def __hash__(self):
        return hash(__class__.__name__)

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __repr__(self):
        return f'{__class__.__name__}'


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
