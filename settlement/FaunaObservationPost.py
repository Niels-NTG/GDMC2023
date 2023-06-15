import numpy as np
import glm
from glm import ivec2, ivec3

from StructureBase import Structure
import settlementTools
import vectorTools
import worldTools
from Node import Node
from RootNode import RootNode
from gdpc.gdpc import Rect
from structures.gamma.medium_hub.medium_hub import MediumHub


class FaunaObservationPost:

    def __init__(
        self,
        rng: np.random.Generator = np.random.default_rng(),
    ):

        FaunaObservationPost.buildVillageObservationPost(rng)

    @staticmethod
    def buildVillageObservationPost(rng: np.random.Generator = np.random.default_rng()):
        settlementType = 'villageObservationPost'

        nodeList: list[Node] = []

        explorationContant = 4.0
        initialSettlementProperties = {
            'workerSize': 0,
            'kitchenSize': 0,
            'foodSize': 0,
            'archiveSize': 0,
        }

        numberOfVillagers = 22
        personelRequirement = 4 + numberOfVillagers
        kitchenRequirement = personelRequirement
        foodRequirement = personelRequirement
        archiveRequirement = max(1, numberOfVillagers // 6)
        storageRequirement = max(2, personelRequirement // 4)

        def multiObjectiveBookKeeper(node: Node):
            node.bookKeepingProperties['workerSize'] += node.structure.customProperties.get('workerCapacity', 0)
            node.bookKeepingProperties['kitchenSize'] += node.structure.customProperties.get('kitchenCapacity', 0)
            node.bookKeepingProperties['foodSize'] += node.structure.customProperties.get('foodUnits', 0)
            node.bookKeepingProperties['archiveSize'] += node.structure.customProperties.get('archiveCapacity', 0)

        def villageObservationPostActionFilter(candidateStructure: Structure) -> bool:
            return True
        def bedsRewardFunction(node: Node) -> float:
            if node.bookKeepingProperties['workerSize'] > personelRequirement:
                return -1
            return node.bookKeepingProperties['workerSize']

        rootNode = RootNode(
            structure=MediumHub(
                facing=rng.integers(4),
                settlementType=settlementType,
                position=ivec3(0, 0, 0),
            ),
            rng=rng,
            actionFilter=villageObservationPostActionFilter,
            rewardFunction=bedsRewardFunction,
            settlementType=settlementType,
            bookKeepingProperties=initialSettlementProperties,
            bookKeeper=multiObjectiveBookKeeper,
        )
        nodeListPart = settlementTools.runSearcher(
            rootNode=rootNode,
            rng=rng,
            targetName=f'{settlementType}_beds',
            explorationConstant=explorationContant,
        )
        nodeList.extend(nodeListPart)
        rootNode = nodeList[0]

        def kitchenRewardFunction(node: Node) -> float:
            if node.bookKeepingProperties['kitchenSize'] > kitchenRequirement:
                return -1
            return node.bookKeepingProperties['kitchenSize']

        rootNode.rewardFunction = kitchenRewardFunction
        nodeListPart = settlementTools.runSearcher(
            rootNode=rootNode,
            rng=rng,
            targetName=f'{settlementType}_kitchens',
            explorationConstant=explorationContant,
        )
        nodeList.extend(nodeListPart)

        def foodSourceRewardFunction(node: Node) -> float:
            if node.bookKeepingProperties['foodSize'] > foodRequirement:
                return -1
            return node.bookKeepingProperties['foodSize']

        rootNode.rewardFunction = foodSourceRewardFunction
        nodeListPart = settlementTools.runSearcher(
            rootNode=rootNode,
            rng=rng,
            targetName=f'{settlementType}_food',
            explorationConstant=explorationContant,
        )
        nodeList.extend(nodeListPart)

        def archiveRewardFunction(node: Node) -> float:
            if node.bookKeepingProperties['archiveSize'] > archiveRequirement:
                return -1
            return node.bookKeepingProperties['archiveSize']

        rootNode.rewardFunction = archiveRewardFunction
        nodeListPart = settlementTools.runSearcher(
            rootNode=rootNode,
            rng=rng,
            targetName=f'{settlementType}_archive',
            explorationConstant=explorationContant,
        )
        nodeList.extend(nodeListPart)

    @staticmethod
    def findDrowned() -> list[worldTools.EntitiesPerArea]:
        foundDrowners = FaunaObservationPost.selectAreas(worldTools.getEntitiesPerGrid(
            query={'type': 'drowned'},
            includeData=False,
            gridSize=ivec2(32, 32),
        ))
        if len(foundDrowners) > 0:
            return foundDrowners

    @staticmethod
    def findVillagers() -> list[worldTools.EntitiesPerArea]:
        return FaunaObservationPost.selectAreas(worldTools.getEntitiesPerGrid(
            query={'type': 'villager'},
            includeData=False,
            gridSize=ivec2(128, 128),
        ))

    @staticmethod
    def findPillagerOutpost() -> list[worldTools.EntitiesPerArea]:
        return FaunaObservationPost.selectAreas(worldTools.getEntitiesPerGrid(
            query={'type': 'pillager'},
            includeData=False,
            gridSize=ivec2(32, 32),
        ))

    @staticmethod
    def findWitchHut() -> list[worldTools.EntitiesPerArea]:
        return FaunaObservationPost.selectAreas(worldTools.getEntitiesPerGrid(
            query={'type': 'witch'},
            includeData=False,
            gridSize=ivec2(32, 32),
        ))

    @staticmethod
    def findGlowSquids() -> list[worldTools.EntitiesPerArea]:
        return FaunaObservationPost.selectAreas(worldTools.getEntitiesPerGrid(
            query={'type': 'glow_squid'},
            includeData=True,
            gridSize=ivec2(8, 8),
        ))

    @staticmethod
    def selectAreas(entityListPerArea: list[worldTools.EntitiesPerArea]) -> list[worldTools.EntitiesPerArea]:
        if len(entityListPerArea) == 0:
            return []
        sortedAreas: list[worldTools.EntitiesPerArea] = sorted(entityListPerArea, key=len)
        entitiesCounts: list[int] = []
        for entitiesPerArea in sortedAreas:
            entitiesCounts.append(len(entitiesPerArea))
        ninetyPercentileValue = np.percentile(entitiesCounts, 90, method='nearest')
        ninetyPercentileIndex = entitiesCounts.index(ninetyPercentileValue)
        # Return last if no ninety percentile areas exist for some reason.
        # an example of overly defensive programming.
        if ninetyPercentileIndex == -1:
            return sortedAreas[-1:]

        # Get areas in the ninety percentile range, then sort them in the
        # original order where the areas are adjecent to each other.
        ninetyPercentileAreas = sortedAreas[ninetyPercentileIndex:]
        orderedAreas = []
        for entitiesPerArea in entityListPerArea:
            if entitiesPerArea in ninetyPercentileAreas:
                orderedAreas.append(entitiesPerArea)
        return orderedAreas
