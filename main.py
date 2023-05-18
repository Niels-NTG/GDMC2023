from typing import Callable

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
        if index + 1 < len(nodeList):
            nextNode = nodeList[index + 1]
        node.finalize(nextNode, routeName)


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

targetRedMushroomBlockPosition = worldTools.getRandomSurfacePosition(globalRNG)
globals.editor.placeBlock(
    position=targetRedMushroomBlockPosition,
    block=Block('red_mushroom_block')
)
print(f'Red mushroom block at {targetRedMushroomBlockPosition}')

targetOrangeConcretePosition = worldTools.getRandomSurfacePosition(globalRNG)
globals.editor.placeBlock(
    position=targetOrangeConcretePosition,
    block=Block('orange_concrete')
)
print(f'Orange concrete block at {targetOrangeConcretePosition}')

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
    return float(np.sum(np.abs(targetGoldBlockPosition - node.structure.boxInWorldSpace.middle) * (1, 4, 1)))


def rewardFunction2(node: Node) -> float:
    return float(np.sum(np.abs(targetEmeraldBlockPosition - node.structure.boxInWorldSpace.middle) * (1, 4, 1)))


def rewardFunction3(node: Node) -> float:
    return float(np.sum(np.abs(targetRedMushroomBlockPosition - node.structure.boxInWorldSpace.middle) * (1, 4, 1)))


def rewardFunction4(node: Node) -> float:
    return float(np.sum(np.abs(targetOrangeConcretePosition - node.structure.boxInWorldSpace.middle) * (1, 4, 1)))


# TODO also implement custom isTerminalFunction

explorationConstant = np.sqrt(globals.buildarea.area) // 10
print(f'exploration constant: {explorationConstant}')

rootNode = Node(
    structure=rootStructure,
    rng=globalRNG,
    rewardFunction=rewardFunction1
)
searcher1 = MCTS(iterationLimit=40000, rolloutPolicy=mctsRolloutPolicy, explorationConstant=explorationConstant, rng=globalRNG)
searcher1.search(initialState=rootNode)
nodeList1: list[Node] = searcher1.getBestRoute()
finalizeTrace(nodeList1, 'route1')

searcher2 = MCTS(iterationLimit=40000, rolloutPolicy=mctsRolloutPolicy, explorationConstant=explorationConstant, rng=globalRNG)
rootNode2 = findConnectionNode(rewardFunction=rewardFunction2)
rootNode2.rewardFunction = rewardFunction2
searcher2.search(initialState=rootNode2)
nodeList2: list[Node] = searcher2.getBestRoute()
finalizeTrace(nodeList2, 'route2')

searcher3 = MCTS(iterationLimit=40000, rolloutPolicy=mctsRolloutPolicy, explorationConstant=explorationConstant, rng=globalRNG)
rootNode3 = findConnectionNode(rewardFunction=rewardFunction3)
rootNode3.rewardFunction = rewardFunction3
searcher3.search(initialState=rootNode3)
nodeList3: list[Node] = searcher3.getBestRoute()
finalizeTrace(nodeList3, 'route3')

searcher4 = MCTS(iterationLimit=40000, rolloutPolicy=mctsRolloutPolicy, explorationConstant=explorationConstant, rng=globalRNG)
rootNode4 = findConnectionNode(rewardFunction=rewardFunction4)
rootNode4.rewardFunction = rewardFunction4
searcher4.search(initialState=rootNode4)
nodeList4: list[Node] = searcher4.getBestRoute()
finalizeTrace(nodeList4, 'route4')

placeNodes()

