import re

import numpy as np
from glm import ivec2, ivec3

import globals
from StructureBase import Structure
from gdpc.gdpc.vector_tools import Box, Rect, loop2D
from gdpc.gdpc.block import Block
from gdpc.gdpc import lookup

DEFAULT_HEIGHTMAP_TYPE: str = 'MOTION_BLOCKING_NO_PLANTS'


class PlacementInstruction:

    def __init__(
        self,
        position: ivec3 = None,
        block: Block = None
    ):
        self.position = position
        self.block = block

    def __hash__(self):
        return hash(self.position)


def isStructureInsideBuildArea(structure: Structure) -> bool:
    return isBoxInsideBuildArea(structure.boxInWorldSpace)


def isBoxInsideBuildArea(box: Box) -> bool:
    return (
        box.begin.x >= globals.buildarea.begin.x and
        box.begin.z >= globals.buildarea.begin.y and
        box.end.x <= globals.buildarea.last.x and
        box.end.z <= globals.buildarea.last.y
    )


def isStructureTouchingSurface(
    structure: Structure,
    heightmapType: str = DEFAULT_HEIGHTMAP_TYPE
) -> bool:
    return isBoxTouchingSurface(box=structure.boxInWorldSpace, heightmapType=heightmapType)


def isBoxTouchingSurface(
    box: Box,
    heightmapType: str = DEFAULT_HEIGHTMAP_TYPE
) -> bool:
    floorRect = box.toRect()
    for point in loop2D(floorRect.begin, floorRect.end):
        if getHeightAt(pos=point, heightmapType=heightmapType) > box.offset.y:
            return True
    return False


def getHeightAt(
    pos: ivec3 | ivec2,
    heightmapType: str = DEFAULT_HEIGHTMAP_TYPE
) -> int:
    # WORLD_SURFACE
    # Stores the Y-level of the highest non-air block.
    #
    # OCEAN_FLOOR
    # Stores the Y-level of the highest block whose material blocks motion. Used only on the server side.
    #
    # MOTION_BLOCKING
    # Stores the Y-level of the highest block whose material blocks motion or blocks that contains a
    # fluid (water, lava, or waterlogging blocks).
    #
    # MOTION_BLOCKING_NO_LEAVES
    # Stores the Y-level of the highest block whose material blocks motion, or blocks that contains a
    # fluid (water, lava, or waterlogging blocks), except various leaves. Used only on the server side.
    if isinstance(pos, ivec3):
        pos = ivec2(pos.x, pos.z)
    heightmap = globals.editor.worldSlice.heightmaps[heightmapType]

    positionRelativeToWorldSlice = (pos - globals.editor.worldSlice.rect.offset)
    return heightmap[positionRelativeToWorldSlice.x, positionRelativeToWorldSlice.y]


def getSurfacePositionAt(
    pos: ivec3 | ivec2,
    heightmapType: str = DEFAULT_HEIGHTMAP_TYPE
) -> ivec3:
    if isinstance(pos, ivec3):
        pos = ivec2(pos.x, pos.z)
    return ivec3(
        pos.x,
        getHeightAt(pos=pos, heightmapType=heightmapType),
        pos.y
    )


def getRandomSurfacePosition(
    rng=np.random.default_rng(),
    heightmapType: str = DEFAULT_HEIGHTMAP_TYPE
) -> ivec3:
    startPosition = ivec3(
        globals.buildarea.offset.x + rng.choice(globals.buildarea.size.x),
        0,
        globals.buildarea.offset.y + rng.choice(globals.buildarea.size.y)
    )
    startPosition.y = getHeightAt(startPosition, heightmapType=heightmapType)
    return startPosition


def getRandomSurfacePositionForBox(
    box: Box,
    rng=np.random.default_rng(),
    heightmapType: str = DEFAULT_HEIGHTMAP_TYPE
) -> ivec3:
    box = Box(box.offset, box.size)
    MAX_ATTEMPTS = 128
    for _ in range(MAX_ATTEMPTS):
        pos = getRandomSurfacePosition(rng, heightmapType)
        box.offset = pos
        if isBoxInsideBuildArea(box):
            return pos
    raise Exception('Could not fit box inside build area')


def getSapling(
    block: Block = None
) -> Block:
    woodType = re.sub(r'minecraft:|_.+$', '', block.id)
    if woodType == 'mangrove':
        return Block(id='minecraft:mangrove_propagule', states={'stage': '1'})
    if woodType in lookup.WOOD_TYPES:
        return Block(id=f'minecraft:{woodType}_sapling', states={'stage': '1'})


def calculateTreeCuttingCost(
    area: Rect
) -> int:
    diffHeightmap = globals.editor.worldSlice.heightmaps['MOTION_BLOCKING_NO_LEAVES'] - \
                    globals.editor.worldSlice.heightmaps['MOTION_BLOCKING_NO_PLANTS']
    outerArea = area.centeredSubRect(size=area.size + 10)
    outerAreaRelativeToBuildArea = Rect(
        offset=outerArea.offset - globals.editor.worldSlice.rect.offset,
        size=outerArea.size
    )
    diffHeightmap = diffHeightmap[
        outerAreaRelativeToBuildArea.begin.x:outerAreaRelativeToBuildArea.end.x,
        outerAreaRelativeToBuildArea.begin.y:outerAreaRelativeToBuildArea.end.y,
    ]
    return int(np.sum(diffHeightmap))


def getTreeCuttingInstructions(
    area: Rect
) -> list[PlacementInstruction]:
    treeCuttingInstructions: list[PlacementInstruction] = []

    innerArea = area.centeredSubRect(size=area.size + 4)
    outerArea = area.centeredSubRect(size=area.size + 10)

    diffHeightmap = globals.editor.worldSlice.heightmaps['MOTION_BLOCKING'] - \
        globals.editor.worldSlice.heightmaps['MOTION_BLOCKING_NO_PLANTS']

    treePositions = np.argwhere(diffHeightmap > 0)

    rng = np.random.default_rng()

    for xzPos in treePositions:
        pos2DInWorldSpace = ivec2(xzPos[0], xzPos[1]) + globals.editor.worldSlice.rect.offset
        if not outerArea.contains(pos2DInWorldSpace):
            continue
        for y in range(diffHeightmap[xzPos[0], xzPos[1]]):
            pos3D = ivec3(
                pos2DInWorldSpace.x,
                y + globals.editor.worldSlice.heightmaps['MOTION_BLOCKING_NO_PLANTS'][xzPos[0], xzPos[1]],
                pos2DInWorldSpace.y
            )
            block: Block = globals.editor.worldSlice.getBlockGlobal(pos3D)
            if block.id in lookup.PLANT_BLOCKS:
                if not innerArea.contains(pos2DInWorldSpace):
                    if block.id in lookup.LEAVES and rng.random() > 0.25:
                        continue
                    if y == 0 and rng.random() > 0.25 and block.id in lookup.LOGS and \
                            not is2DPositionContainedInNodes(pos=pos2DInWorldSpace, exludeRect=innerArea):
                        replacementSapling = getSapling(block)
                        if replacementSapling:
                            treeCuttingInstructions.append(PlacementInstruction(
                                block=replacementSapling,
                                position=pos3D
                            ))
                            continue
                treeCuttingInstructions.append(PlacementInstruction(
                    block=Block('minecraft:air'),
                    position=pos3D
                ))

    # NOTE: all pre-processing steps are applied, set /gamerule randomTickSpeed to 100, then after a few seconds set
    # it back to the default value of 3 and remove all items with globals.editor.runCommandGlobal('kill @e[type=item]')
    return treeCuttingInstructions


def is2DPositionContainedInNodes(
    pos: ivec2,
    exludeRect: Rect = None
) -> bool:
    # noinspection PyTypeChecker
    if exludeRect and exludeRect.contains(pos):
        return True
    for node in globals.nodeList:
        nodeRect: Rect = node.structure.rectInWorldSpace
        if nodeRect.centeredSubRect(size=nodeRect.size + 4).contains(pos):
            return True
    return False


def facingBlockState(facing: int = 0) -> str:
    facing = facing % 4
    facingStates = ['east', 'south', 'west', 'north']
    return facingStates[facing]
