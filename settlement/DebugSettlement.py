import numpy as np
from glm import ivec3

import globals
import worldTools
from Node import Node
from RootNode import RootNode
from gdpc.gdpc import Block
import settlementTools
from structures.gamma.tower_hub.tower_hub import TowerHub


class DebugSettlement:

    def __init__(
        self,
        rng: np.random.Generator = np.random.default_rng()
    ):

        self.rng = rng

        targets = [
            (worldTools.getRandomSurfacePosition(rng), Block('gold_block')),
            (worldTools.getRandomSurfacePosition(rng), Block('emerald_block')),
            (worldTools.getRandomSurfacePosition(rng), Block('red_mushroom_block')),
            (worldTools.getRandomSurfacePosition(rng), Block('iron_block')),
        ]
        for pos, block in targets:
            globals.editor.placeBlock(position=pos, block=block)
            print(f'placed {block.id} at {pos}')

        def rewardFunction1(node: Node) -> float:
            return float(np.sum(np.abs(targets[0][0] - node.structure.boxInWorldSpace.middle) * (1, 2, 1)))
        rootNode1 = RootNode(
            structure=TowerHub(
                position=ivec3(0, 0, 0),
                facing=rng.integers(4),
            ),
            rng=rng,
            rewardFunction=rewardFunction1,
        )
        settlementTools.runSearcher(
            rootNode=rootNode1,
            rng=rng,
            targetName=targets[0][1].id,
            explorationConstant=settlementTools.explorationConstantWorldScale(),
        )

        def rewardFunction2(node: Node) -> float:
            return float(np.sum(np.abs(targets[1][0] - node.structure.boxInWorldSpace.middle) * (1, 2, 1)))
        rootNode2 = settlementTools.findConnectionNodeGlobal(rewardFunction=rewardFunction2)
        rootNode2.rewardFunction = rewardFunction2
        settlementTools.runSearcher(
            rootNode=rootNode2,
            rng=rng,
            targetName=targets[1][1].id,
            explorationConstant=settlementTools.explorationConstantWorldScale(),
        )

        def rewardFunction3(node: Node) -> float:
            return float(np.sum(np.abs(targets[2][0] - node.structure.boxInWorldSpace.middle) * (1, 2, 1)))
        rootNode3 = settlementTools.findConnectionNodeGlobal(rewardFunction=rewardFunction3)
        rootNode3.rewardFunction = rewardFunction3
        settlementTools.runSearcher(
            rootNode=rootNode3,
            rng=rng,
            targetName=targets[2][1].id,
            explorationConstant=settlementTools.explorationConstantWorldScale(),
        )

        def rewardFunction4(node: Node) -> float:
            return float(np.sum(np.abs(targets[3][0] - node.structure.boxInWorldSpace.middle) * (1, 2, 1)))
        rootNode4 = settlementTools.findConnectionNodeGlobal(rewardFunction=rewardFunction4)
        rootNode4.rewardFunction = rewardFunction4
        settlementTools.runSearcher(
            rootNode=rootNode4,
            rng=rng,
            targetName=targets[3][1].id,
            explorationConstant=settlementTools.explorationConstantWorldScale(),
        )
