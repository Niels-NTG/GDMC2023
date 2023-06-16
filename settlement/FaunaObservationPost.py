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

        FaunaObservationPost.buildPillagerObservationPost(rng)

        FaunaObservationPost.buildWitchObservationPost(rng)

    @staticmethod
    def buildVillageObservationPost(rng: np.random.Generator = np.random.default_rng()):
        settlementType = 'villageObservationPost'

        nodeList: list[Node] = []

        areasWithVillagers = FaunaObservationPost.findVillagers()
        if len(areasWithVillagers) == 0:
            return
        topArea = max(areasWithVillagers, key=len)
        topAreaRect: Rect = topArea.area.toRect()
        scanRadius = 200
        villageAreas: list[Rect] = []
        numberOfVillagers = len(topArea)
        for areaWithVillagers in areasWithVillagers:
            areaRect: Rect = areaWithVillagers.area.toRect()
            if areaWithVillagers is topAreaRect:
                continue
            if glm.distance(areaRect.center.to_tuple(), topAreaRect.center.to_tuple()) < scanRadius:
                villageAreas.append(areaRect)
                numberOfVillagers += len(areaWithVillagers)
        villageRect: Rect = vectorTools.mergeRects(villageAreas)
        outerRect: Rect = villageRect.centeredSubRect(size=villageRect.size + 256)

        print(f'Found village at {villageRect.middle} with {numberOfVillagers} villagers')
        print('Starting construction of villager observation post…')

        initialSettlementProperties = {
            'workerSize': 0,
            'kitchenSize': 0,
            'foodSize': 0,
            'archiveSize': 0,
            'storageSize': 0,
            'observationSize': 0,
            'exitSize': 0,
        }

        personelRequirement = 4 + numberOfVillagers
        kitchenRequirement = personelRequirement
        foodRequirement = personelRequirement
        archiveRequirement = max(1, numberOfVillagers // 8)
        storageRequirement = max(2, personelRequirement // 8)
        observationRequirement = 1
        exitRequirement = rng.integers(3, 6)

        def multiObjectiveBookKeeper(node: Node):
            node.bookKeepingProperties['workerSize'] += node.structure.customProperties.get('workerCapacity', 0)
            node.bookKeepingProperties['kitchenSize'] += node.structure.customProperties.get('kitchenCapacity', 0)
            node.bookKeepingProperties['foodSize'] += node.structure.customProperties.get('foodUnits', 0)
            node.bookKeepingProperties['archiveSize'] += node.structure.customProperties.get('archiveCapacity', 0)
            node.bookKeepingProperties['storageSize'] += node.structure.customProperties.get('storageCapacity', 0)
            node.bookKeepingProperties['observationSize'] += \
                node.structure.customProperties.get('observationCapacity', 0)
            node.bookKeepingProperties['exitSize'] += node.structure.customProperties.get('exit', 0)

        def villageObservationPostActionFilter(candidateStructure: Structure) -> bool:
            # noinspection PyTypeChecker
            return not villageRect.collides(candidateStructure.rectInWorldSpace) and \
                    outerRect.collides(candidateStructure.rectInWorldSpace)

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
            explorationConstant=np.sqrt(personelRequirement) / 1.4,
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
            explorationConstant=np.sqrt(kitchenRequirement) / 2,
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
            explorationConstant=np.sqrt(foodRequirement) / 1.8,
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
            explorationConstant=np.sqrt(archiveRequirement) / 2,
        )
        nodeList.extend(nodeListPart)

        def storageRewardFunction(node: Node) -> float:
            if node.bookKeepingProperties['storageSize'] > storageRequirement:
                return -1
            return node.bookKeepingProperties['storageSize']

        rootNode.rewardFunction = storageRewardFunction
        nodeListPart = settlementTools.runSearcher(
            rootNode=rootNode,
            rng=rng,
            targetName=f'{settlementType}_storage',
            explorationConstant=np.sqrt(storageRequirement) / 2,
        )
        nodeList.extend(nodeListPart)

        def observationRewardFunction(node: Node) -> float:
            if node.bookKeepingProperties['observationSize'] > observationRequirement:
                return -1
            return node.bookKeepingProperties['observationSize']

        rootNode.rewardFunction = observationRewardFunction
        nodeListPart = settlementTools.runSearcher(
            rootNode=rootNode,
            rng=rng,
            targetName=f'{settlementType}_observation',
            explorationConstant=0.8,
        )
        nodeList.extend(nodeListPart)

        def exitRewardFunction(node: Node) -> float:
            if node.bookKeepingProperties['exitSize'] > exitRequirement:
                return -1
            return node.bookKeepingProperties['exitSize'] * 100

        rootNode.rewardFunction = exitRewardFunction
        nodeListPart = settlementTools.runSearcher(
            rootNode=rootNode,
            rng=rng,
            targetName=f'{settlementType}_exit',
            explorationConstant=np.sqrt(exitRequirement) / 3.2,
        )
        nodeList.extend(nodeListPart)

        print('Finished construction of villager observation post')

    @staticmethod
    def buildPillagerObservationPost(rng: np.random.Generator = np.random.default_rng()):
        settlementType = 'villageObservationPost'

        nodeList: list[Node] = []

        areasWithPillagers = FaunaObservationPost.findPillagerOutpost()
        if len(areasWithPillagers) == 0:
            return
        topArea = max(areasWithPillagers, key=len)
        topAreaRect: Rect = topArea.area.toRect()
        scanRadius = 200
        villageAreas: list[Rect] = []
        numberOfVillagers = len(topArea)
        for areaWithVillagers in areasWithPillagers:
            areaRect: Rect = areaWithVillagers.area.toRect()
            if areaWithVillagers is topAreaRect:
                continue
            if glm.distance(areaRect.center.to_tuple(), topAreaRect.center.to_tuple()) < scanRadius:
                villageAreas.append(areaRect)
                numberOfVillagers += len(areaWithVillagers)
        villageRect: Rect = vectorTools.mergeRects(villageAreas)
        outerRect: Rect = villageRect.centeredSubRect(size=villageRect.size + 256)

        print(f'Found pillager settlement at {villageRect.middle} with {numberOfVillagers} pillagers')
        print('Starting construction of pillager observation post…')

        initialSettlementProperties = {
            'workerSize': 0,
            'kitchenSize': 0,
            'foodSize': 0,
            'archiveSize': 0,
            'storageSize': 0,
            'observationSize': 0,
            'exitSize': 0,
        }

        personelRequirement = 4 + numberOfVillagers
        kitchenRequirement = personelRequirement
        foodRequirement = personelRequirement
        archiveRequirement = max(1, numberOfVillagers // 10)
        storageRequirement = max(2, personelRequirement // 8)
        observationRequirement = 1
        exitRequirement = rng.integers(3, 6)

        def multiObjectiveBookKeeper(node: Node):
            node.bookKeepingProperties['workerSize'] += node.structure.customProperties.get('workerCapacity', 0)
            node.bookKeepingProperties['kitchenSize'] += node.structure.customProperties.get('kitchenCapacity', 0)
            node.bookKeepingProperties['foodSize'] += node.structure.customProperties.get('foodUnits', 0)
            node.bookKeepingProperties['archiveSize'] += node.structure.customProperties.get('archiveCapacity', 0)
            node.bookKeepingProperties['storageSize'] += node.structure.customProperties.get('storageCapacity', 0)
            node.bookKeepingProperties['observationSize'] += \
                node.structure.customProperties.get('observationCapacity', 0)
            node.bookKeepingProperties['exitSize'] += node.structure.customProperties.get('exit', 0)

        def villageObservationPostActionFilter(candidateStructure: Structure) -> bool:
            # noinspection PyTypeChecker
            return not villageRect.collides(candidateStructure.rectInWorldSpace) and \
                    outerRect.collides(candidateStructure.rectInWorldSpace)

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
            explorationConstant=np.sqrt(personelRequirement) / 1.4,
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
            explorationConstant=np.sqrt(kitchenRequirement) / 2,
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
            explorationConstant=np.sqrt(foodRequirement) / 1.8,
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
            explorationConstant=np.sqrt(archiveRequirement) / 2,
        )
        nodeList.extend(nodeListPart)

        def storageRewardFunction(node: Node) -> float:
            if node.bookKeepingProperties['storageSize'] > storageRequirement:
                return -1
            return node.bookKeepingProperties['storageSize']

        rootNode.rewardFunction = storageRewardFunction
        nodeListPart = settlementTools.runSearcher(
            rootNode=rootNode,
            rng=rng,
            targetName=f'{settlementType}_storage',
            explorationConstant=np.sqrt(storageRequirement) / 2,
        )
        nodeList.extend(nodeListPart)

        def observationRewardFunction(node: Node) -> float:
            if node.bookKeepingProperties['observationSize'] > observationRequirement:
                return -1
            return node.bookKeepingProperties['observationSize']

        rootNode.rewardFunction = observationRewardFunction
        nodeListPart = settlementTools.runSearcher(
            rootNode=rootNode,
            rng=rng,
            targetName=f'{settlementType}_observation',
            explorationConstant=0.8,
        )
        nodeList.extend(nodeListPart)

        def exitRewardFunction(node: Node) -> float:
            if node.bookKeepingProperties['exitSize'] > exitRequirement:
                return -1
            return node.bookKeepingProperties['exitSize'] * 100

        rootNode.rewardFunction = exitRewardFunction
        nodeListPart = settlementTools.runSearcher(
            rootNode=rootNode,
            rng=rng,
            targetName=f'{settlementType}_exit',
            explorationConstant=np.sqrt(exitRequirement) / 1.8,
        )
        nodeList.extend(nodeListPart)

        print('Finished construction of pillager observation post')

    @staticmethod
    def buildWitchObservationPost(rng: np.random.Generator = np.random.default_rng()):
        settlementType = 'villageObservationPost'

        nodeList: list[Node] = []

        areasWithPillagers = FaunaObservationPost.findWitchHut()
        if len(areasWithPillagers) == 0:
            return
        topArea = max(areasWithPillagers, key=len)
        topAreaRect: Rect = topArea.area.toRect()
        scanRadius = 200
        villageAreas: list[Rect] = []
        numberOfVillagers = len(topArea)
        for areaWithVillagers in areasWithPillagers:
            areaRect: Rect = areaWithVillagers.area.toRect()
            if areaWithVillagers is topAreaRect:
                continue
            if glm.distance(areaRect.center.to_tuple(), topAreaRect.center.to_tuple()) < scanRadius:
                villageAreas.append(areaRect)
                numberOfVillagers += len(areaWithVillagers)
        villageRect: Rect = vectorTools.mergeRects(villageAreas)
        outerRect: Rect = villageRect.centeredSubRect(size=villageRect.size + 256)

        print(f'Found witch settlement at {villageRect.middle}')
        print('Starting construction of witch observation post…')

        initialSettlementProperties = {
            'workerSize': 0,
            'kitchenSize': 0,
            'foodSize': 0,
            'archiveSize': 0,
            'storageSize': 0,
            'observationSize': 0,
            'exitSize': 0,
        }

        personelRequirement = 4 + numberOfVillagers
        kitchenRequirement = personelRequirement
        foodRequirement = personelRequirement
        archiveRequirement = max(1, numberOfVillagers // 10)
        storageRequirement = max(2, personelRequirement // 8)
        observationRequirement = 1
        exitRequirement = rng.integers(3, 6)

        def multiObjectiveBookKeeper(node: Node):
            node.bookKeepingProperties['workerSize'] += node.structure.customProperties.get('workerCapacity', 0)
            node.bookKeepingProperties['kitchenSize'] += node.structure.customProperties.get('kitchenCapacity', 0)
            node.bookKeepingProperties['foodSize'] += node.structure.customProperties.get('foodUnits', 0)
            node.bookKeepingProperties['archiveSize'] += node.structure.customProperties.get('archiveCapacity', 0)
            node.bookKeepingProperties['storageSize'] += node.structure.customProperties.get('storageCapacity', 0)
            node.bookKeepingProperties['observationSize'] += \
                node.structure.customProperties.get('observationCapacity', 0)
            node.bookKeepingProperties['exitSize'] += node.structure.customProperties.get('exit', 0)

        def villageObservationPostActionFilter(candidateStructure: Structure) -> bool:
            # noinspection PyTypeChecker
            return not villageRect.collides(candidateStructure.rectInWorldSpace) and \
                    outerRect.collides(candidateStructure.rectInWorldSpace)

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
            explorationConstant=np.sqrt(personelRequirement) / 1.4,
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
            explorationConstant=np.sqrt(kitchenRequirement) / 2,
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
            explorationConstant=np.sqrt(foodRequirement) / 1.8,
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
            explorationConstant=np.sqrt(archiveRequirement) / 2,
        )
        nodeList.extend(nodeListPart)

        def storageRewardFunction(node: Node) -> float:
            if node.bookKeepingProperties['storageSize'] > storageRequirement:
                return -1
            return node.bookKeepingProperties['storageSize']

        rootNode.rewardFunction = storageRewardFunction
        nodeListPart = settlementTools.runSearcher(
            rootNode=rootNode,
            rng=rng,
            targetName=f'{settlementType}_storage',
            explorationConstant=np.sqrt(storageRequirement) / 2,
        )
        nodeList.extend(nodeListPart)

        def observationRewardFunction(node: Node) -> float:
            if node.bookKeepingProperties['observationSize'] > observationRequirement:
                return -1
            return node.bookKeepingProperties['observationSize']

        rootNode.rewardFunction = observationRewardFunction
        nodeListPart = settlementTools.runSearcher(
            rootNode=rootNode,
            rng=rng,
            targetName=f'{settlementType}_observation',
            explorationConstant=0.8,
        )
        nodeList.extend(nodeListPart)

        def exitRewardFunction(node: Node) -> float:
            if node.bookKeepingProperties['exitSize'] > exitRequirement:
                return -1
            return node.bookKeepingProperties['exitSize'] * 100

        rootNode.rewardFunction = exitRewardFunction
        nodeListPart = settlementTools.runSearcher(
            rootNode=rootNode,
            rng=rng,
            targetName=f'{settlementType}_exit',
            explorationConstant=np.sqrt(exitRequirement) / 2,
        )
        nodeList.extend(nodeListPart)

        print('Finished construction of witch observation post')

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
            gridSize=ivec2(256, 256),
        ))

    @staticmethod
    def findPillagerOutpost() -> list[worldTools.EntitiesPerArea]:
        return FaunaObservationPost.selectAreas(worldTools.getEntitiesPerGrid(
            query={'type': 'pillager'},
            includeData=False,
            gridSize=ivec2(128, 128),
        ))

    @staticmethod
    def findWitchHut() -> list[worldTools.EntitiesPerArea]:
        return FaunaObservationPost.selectAreas(worldTools.getEntitiesPerGrid(
            query={'type': 'witch'},
            includeData=False,
            gridSize=ivec2(128, 128),
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
