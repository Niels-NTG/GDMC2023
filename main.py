from typing import Callable

import glm
import numpy as np
from glm import ivec2, ivec3

from MCTS.mcts import MCTS

from gdpc.gdpc.block import Block

import globals
import worldTools
from Node import Node
from structures.debug.narrow_hub.narrow_hub import NarrowHub

globals.initialize()



def mctsRolloutPolicy(state: Node, rng: np.random.Generator = np.random.default_rng()) -> float:
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


globalRNG = np.random.default_rng(2190828244)

targetGoldBlockPosition = worldTools.getRandomSurfacePosition(globalRNG)
globals.editor.placeBlock(
    position=targetGoldBlockPosition,
    block=Block('gold_block')
)
print(f'Gold block at {targetGoldBlockPosition}')

targetEmeraldBlockPosition = worldTools.getRandomSurfacePosition(globalRNG)
globals.editor.placeBlock(
    position=targetEmeraldBlockPosition,
    block=Block('emerald_block')
)
print(f'Emerald block at {targetEmeraldBlockPosition}')

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
    facing=globalRNG.integers(4),
    position=ivec3(0, 0, 0)
)
rootStructure.position = worldTools.getRandomSurfacePosition(globalRNG)
globals.editor.placeBlockGlobal(
    position=rootStructure.position,
    block=Block('diamond_block')
)


def rewardFunction1(node: Node) -> float:
    return glm.distance(targetGoldBlockPosition.to_tuple(), node.structure.boxInWorldSpace.middle.to_tuple())


def rewardFunction2(node: Node) -> float:
    return glm.distance(targetEmeraldBlockPosition.to_tuple(), node.structure.boxInWorldSpace.middle.to_tuple())


# TODO also implement custom isTerminalFunction

rootNode = Node(
    structure=rootStructure,
    rng=globalRNG,
    rewardFunction=rewardFunction1
)
# TODO change MCTS to use np.random instead of random library
searcher1 = MCTS(iterationLimit=10000, rolloutPolicy=mctsRolloutPolicy, explorationConstant=10)
searcher1.search(initialState=rootNode)
nodeList1: list[Node] = searcher1.getBestRoute()
finalizeTrace(nodeList1, 'route1')

searcher2 = MCTS(iterationLimit=10000, rolloutPolicy=mctsRolloutPolicy, explorationConstant=10)
rootNode2 = findConnectionNode(rewardFunction=rewardFunction2)
rootNode2.rewardFunction = rewardFunction2
searcher2.search(initialState=rootNode2)
nodeList2: list[Node] = searcher2.getBestRoute()
finalizeTrace(nodeList2, 'route2')

placeNodes()

