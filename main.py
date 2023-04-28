import numpy as np
from glm import ivec2, ivec3

import MCTS.mcts
from MCTS.mcts import mcts

from gdpc.gdpc.block import Block

import globals
import worldTools
from Node import Node
from structures.debug.narrow_hub.narrow_hub import NarrowHub

globals.initialize()

rng = np.random.default_rng(444992827400221123)

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
                    weights.append(
                        1 - (action.cost / actionCostSum)
                    )
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


def finalizeTrace(nodeList: list[Node]):
    for index, node in enumerate(nodeList):
        nextNode = None
        if index + 1 < len(nodeList) - 1:
            nextNode = nodeList[index + 1]
        node.finalise(nextNode)


def findConnectionNode(rng: np.random.Generator = np.random.default_rng()) -> Node:
    MAX_ATTEMPTS = 128
    # TODO doesn't always work when stairs are involved for some reason
    for _ in range(MAX_ATTEMPTS):
        # TODO out of the open connection nodes, select the one that is nearest the objective
        selectedNode: Node = rng.choice(globals.nodeList)
        if selectedNode.hasOpenSlot():
            return selectedNode
    raise Exception('Could not fit node with open connection slot')


def placeNodes():
    for node in globals.nodeList:
        node.place()
    globals.editor.runCommandGlobal(
        f'fill {globals.buildarea.begin.x} {y} {globals.buildarea.begin.y} {globals.buildarea.last.x} {y} {globals.buildarea.last.y} minecraft:air',

    )
globals.editor.runCommandGlobal('kill @e[type=item]')

globals.editor.loadWorldSlice(rect=globals.buildarea, cache=True)

globals.targetGoldBlockPosition = worldTools.getRandomSurfacePosition(rng=rng)
globals.editor.placeBlock(
    position=globals.targetGoldBlockPosition,
    block=Block('gold_block')
)
print(f'Gold block at {globals.targetGoldBlockPosition}')

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
rootStructure.position = worldTools.getRandomSurfacePositionForBox(box=rootStructure.box, rng=rng)
rootNode = Node(
    structure=rootStructure,
    rng=rng,
)


def mctsRolloutPolicy(state: Node):
    while not state.isTerminal():
        try:
            actions = state.getPossibleActions()
            if len(actions) > 1:
                # Bias actions towards lower costs structures
                actionCostSum = sum(actions)
                weights = []
                for action in actions:
                    weights.append(
                        1 - (action.cost / actionCostSum)
                    )
                weights = weights / np.sum(weights)
                selectedAction = rng.choice(actions, p=weights)
            else:
                selectedAction = actions[0]
        except IndexError:
            raise Exception(f'Non-terminal state has no possible actions: {state}')
        state = state.takeAction(selectedAction)
    return state.getReward()


searcher = mcts(iterationLimit=100000, rolloutPolicy=mctsRolloutPolicy, explorationConstant=10)
searcher.search(initialState=rootNode)


def buildFoundTrace(treeNode: MCTS.mcts.treeNode):
    treeNode.state.place()
    if treeNode.isTerminal:
        return
    bestChild: MCTS.mcts.treeNode = searcher.getBestChild(treeNode, 0)
    buildFoundTrace(bestChild)


buildFoundTrace(searcher.root)
