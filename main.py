from typing import Callable

import glm
import numpy as np
from glm import ivec2, ivec3

from MCTS.mcts import mcts

from gdpc.gdpc.block import Block

import globals
import worldTools
from Node import Node
from structures.debug.narrow_hub.narrow_hub import NarrowHub

globals.initialize()


for y in range(0, 7):
def mctsRolloutPolicy(state: Node):
    while not state.isTerminal():
        try:
            actions = state.getPossibleActions()
            if len(actions) > 1:
                # Bias actions towards lower costs structures
                actionCostSum = sum(actions)
                weights = []
                for action in actions:
                    weights.append(1 - (action.cost / actionCostSum))
                weights = weights / np.sum(weights)
                selectedAction = rng.choice(actions, p=weights)
            else:
                selectedAction = actions[0]
        except IndexError:
            raise Exception(f'Non-terminal state has no possible actions: {state}')
        state = state.takeAction(selectedAction)
    return state.getReward()


def getFoundTrace(searcher: mcts) -> list[Node]:
    nodeList: list[Node] = []
    treeNode = searcher.root
    while not treeNode.isTerminal:
        nodeList.append(treeNode.state)
        treeNode = searcher.getBestChild(treeNode, 0)
    return nodeList


def finalizeTrace(nodeList: list[Node], routeName: str = None):
    for index, node in enumerate(nodeList):
        nextNode = None
        if index + 1 < len(nodeList) - 1:
            nextNode = nodeList[index + 1]
        node.finalise(nextNode, routeName)


def findConnectionNode(
    rewardFunction: Callable[[Node], float] = None
) -> Node:
    candidateNodes: list[Node] = []
    rewards: list[float] = []
    for finalizedNode in globals.nodeList:
        if finalizedNode.hasOpenSlot:
            candidateNodes.append(finalizedNode)
            rewards.append(rewardFunction(finalizedNode))
    if len(candidateNodes) == 0:
        raise Exception('Could not fit node with open connection slot')
    return candidateNodes[np.argmin(rewards)]


def placeNodes():
    # Set random tick speed to zero to prevent any trees from growing while structures are being placed.
    globals.editor.runCommandGlobal('gamerule randomTickSpeed 0')
    for node in globals.nodeList:
        node.doPreProcessingSteps()
    globals.editor.flushBuffer()

    for node in globals.nodeList:
        node.place()

    for node in globals.nodeList:
        node.doPostProcessingSteps()

    # Set random tick speed to 300 for a little bit to speed up tree growth
    globals.editor.runCommandGlobal('gamerule randomTickSpeed 300')
    globals.editor.flushBuffer()
    globals.editor.runCommandGlobal('gamerule randomTickSpeed 3')
    globals.editor.runCommandGlobal('kill @e[type=item]')


rng = np.random.default_rng(807414098708321)

globals.targetGoldBlockPosition = worldTools.getRandomSurfacePosition(rng)
globals.editor.placeBlock(
    position=globals.targetGoldBlockPosition,
    block=Block('gold_block')
)
print(f'Gold block at {globals.targetGoldBlockPosition}')

globals.targetEmeraldBlockPosition = worldTools.getRandomSurfacePosition(rng)
globals.editor.placeBlock(
    position=globals.targetEmeraldBlockPosition,
    block=Block('emerald_block')
)
print(f'Emerald block at {globals.targetEmeraldBlockPosition}')

globals.editor.placeBlock(
    position=worldTools.getSurfacePositionAt(globals.buildarea.begin),
    block=Block('red_concrete')
)
globals.editor.placeBlock(
    position=worldTools.getSurfacePositionAt(globals.buildarea.last),
    block=Block('purple_concrete')
)
globals.editor.placeBlock(
    position=worldTools.getSurfacePositionAt(ivec2(
        globals.buildarea.begin.x,
        globals.buildarea.last.y
    )),
    block=Block('purple_concrete')
)
globals.editor.placeBlock(
    position=worldTools.getSurfacePositionAt(ivec2(
        globals.buildarea.last.x,
        globals.buildarea.begin.y
    )),
    block=Block('purple_concrete')
)

rootStructure = NarrowHub(
    facing=rng.integers(4),
    position=ivec3(0, 0, 0)
)
rootStructure.position = worldTools.getRandomSurfacePosition(rng)
globals.editor.placeBlockGlobal(
    position=rootStructure.position,
    block=Block('diamond_block')
)


def rewardFunction1(node: Node) -> float:
    return glm.distance(globals.targetGoldBlockPosition.to_tuple(), node.structure.boxInWorldSpace.middle.to_tuple())


def rewardFunction2(node: Node) -> float:
    return glm.distance(globals.targetEmeraldBlockPosition.to_tuple(), node.structure.boxInWorldSpace.middle.to_tuple())


# TODO also implement custom isTerminalFunction


rootNode = Node(
    structure=rootStructure,
    rng=rng,
    rewardFunction=rewardFunction1
)
searcher1 = mcts(iterationLimit=10000, rolloutPolicy=mctsRolloutPolicy, explorationConstant=10)
searcher1.search(initialState=rootNode)
nodeList1: list[Node] = getFoundTrace(searcher1)
finalizeTrace(nodeList1, 'route1')

searcher2 = mcts(iterationLimit=10000, rolloutPolicy=mctsRolloutPolicy, explorationConstant=10)
rootNode2 = findConnectionNode(rewardFunction=rewardFunction2)
rootNode2.rewardFunction = rewardFunction2
searcher2.search(initialState=rootNode2)
nodeList2: list[Node] = getFoundTrace(searcher2)
finalizeTrace(nodeList2, 'route2')

placeNodes()

