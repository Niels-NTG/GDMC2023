import numpy as np

import globals
import worldTools
from MCTS.mcts import MCTS
from Node import Node
from RootNode import RootNode
from gdpc.gdpc import Block
import settlementTools


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
            nodeRewardFunction=rewardFunction1,
            rng=rng,
        )
        self.runSearcher(rootNode1, targets[0][1].id)

        def rewardFunction2(node: Node) -> float:
            return float(np.sum(np.abs(targets[1][0] - node.structure.boxInWorldSpace.middle) * (1, 2, 1)))
        rootNode2 = settlementTools.findConnectionNode(rewardFunction=rewardFunction2)
        rootNode2.rewardFunction = rewardFunction2
        self.runSearcher(rootNode2, targets[1][1].id)

        def rewardFunction3(node: Node) -> float:
            return float(np.sum(np.abs(targets[2][0] - node.structure.boxInWorldSpace.middle) * (1, 2, 1)))
        rootNode3 = settlementTools.findConnectionNode(rewardFunction=rewardFunction3)
        rootNode3.rewardFunction = rewardFunction3
        self.runSearcher(rootNode3, targets[2][1].id)

        def rewardFunction4(node: Node) -> float:
            return float(np.sum(np.abs(targets[3][0] - node.structure.boxInWorldSpace.middle) * (1, 2, 1)))
        rootNode4 = settlementTools.findConnectionNode(rewardFunction=rewardFunction4)
        rootNode4.rewardFunction = rewardFunction4
        self.runSearcher(rootNode4, targets[3][1].id)

    def runSearcher(self, rootNode: Node, targetName: str):
        searcher = MCTS(
            iterationLimit=40000,
            rolloutPolicy=settlementTools.mctsRolloutPolicy,
            explorationConstant=settlementTools.explorationConstant(),
            rng=self.rng,
        )
        searcher.search(initialState=rootNode)
        nodeList: list[Node] = searcher.getBestRoute()
        settlementTools.finalizeTrace(nodeList, targetName)
