import numpy as np
from glm import ivec2, ivec3

import globals
from StructureBase import Structure
from gdpc.gdpc.vector_tools import Box, loop2D


DEFAULT_HEIGHTMAP_TYPE: str = 'MOTION_BLOCKING_NO_LEAVES'


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


# TODO check if these methods can be memoized (@functools.cache) by providing the worldSlice as function argument
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
