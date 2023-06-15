from __future__ import annotations

from glm import ivec3, ivec2

import globals
from Node import Node, Action
from gdpc.gdpc import Rect
import worldTools
import vectorTools


class RootNode(Node):

    def finalize(self, nextNode: Node = None, routeName: str = None, clearActionCache: bool = False):
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

    def getPossibleActions(self) -> list[Action]:
        if self.possibleActions is not None:
            return self.possibleActions
        possibleActions: list[Action] = []

        sampleSize = max(2, int(worldTools.buildAreaSqrt() // 40))
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
            # Skip if not flat enough
            if locationEvaluation[0] > 10:
                continue

            structurePosition = ivec3(location[0], locationEvaluation[2] + 1, location[1])
            structureRotation = self.rng.integers(4)
            self.structure.position = structurePosition
            self.structure.facing = structureRotation
            # noinspection PyArgumentList
            candidateStructure = type(self.structure)(
                position=structurePosition,
                facing=structureRotation,
                settlementType=self.settlementType,
            )
            structureEvaluation = self.evaluateCandidateNextStructure(candidateStructure)
            if structureEvaluation > 0:
                possibleActions.append(Action(
                    structure=candidateStructure,
                    cost=locationEvaluation[0] + structureEvaluation,
                ))

        self.possibleActions = possibleActions
        return self.possibleActions

    def takeAction(self, action: Action) -> Node:
        return Node(
            structure=action.structure,
            cost=action.cost,
            # Omitted: RootNode does not count as parent
            # parentNode=self,
            # parentConnector=action.connector,
            rewardFunction=self.rewardFunction,
            terminationFunction=self.terminationFunction,
            actionFilter=self.actionFilter,
            settlementType=self.settlementType,
            bookKeepingProperties=self.bookKeepingProperties,
            bookKeeper=self.bookKeeper,
            rng=self.rng,
        )

    def getReward(self) -> float:
        return 1.0
