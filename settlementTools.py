from __future__ import annotations
from typing import Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from Node import Node

import numpy as np

import globals
import worldTools
from MCTS.mcts import MCTS


def runSearcher(
    rootNode: Node,
    rng: np.random.Generator = np.random.default_rng(),
    targetName: str = '',
    iterationLimit: int = 40000,
    explorationConstant: float = 1 / np.sqrt(2),
) -> list[Node]:
    print(f'Start MCTS for {targetName} (iterationLimit: {iterationLimit}, explorationConstant: {explorationConstant})')
    searcher = MCTS(
        iterationLimit=iterationLimit,
        rolloutPolicy=mctsRolloutPolicy,
        explorationConstant=explorationConstant,
        rng=rng,
    )
    searcher.search(initialState=rootNode)
    nodeList: list[Node] = searcher.getBestRoute()
    print(f'Finished running MCTS for {targetName}. A trace of {len(nodeList)} was found.')
    finalizeTrace(nodeList, targetName)
    return nodeList


def explorationConstantWorldScale() -> float:
    return worldTools.buildAreaSqrt() / 10


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
    rewardFunction: Callable[[Node], float] = None,
    nodeList: list[Node] = None,
) -> Node:
    if nodeList is None or len(nodeList) == 0:
        raise Exception('Could not fit node with open connection slot')
    candidateNodes: list[Node] = []
    rewards: list[float] = []
    for finalizedNode in nodeList:
        if finalizedNode.hasOpenSlot:
            candidateNodes.append(finalizedNode)
            rewards.append(rewardFunction(finalizedNode))
    if len(candidateNodes) == 0:
        raise Exception('Could not fit node with open connection slot')
    return candidateNodes[np.argmin(rewards)]


def findConnectionNodeGlobal(
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

    print(globals.nodeList)

    # Clear nodeList to prevent placing nodes multiple times.
    globals.nodeList.clear()
