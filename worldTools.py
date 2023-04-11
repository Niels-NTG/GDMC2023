import numpy as np
from glm import ivec2, ivec3

import globals
from StructureBase import Structure
from gdpc.gdpc.vector_tools import Box


def isStructureInsideBuildArea(structure: Structure) -> bool:
    return isBoxInsideBuildArea(structure.boxInWorldSpace)


def isBoxInsideBuildArea(box: Box) -> bool:
    return (
        box.begin.x >= globals.buildarea.begin.x and
        box.begin.z >= globals.buildarea.begin.y and
        box.end.x <= globals.buildarea.last.x and
        box.end.z <= globals.buildarea.last.y
    )


def getHeightAt(pos: ivec3 | ivec2, heightmapType: str = 'MOTION_BLOCKING_NO_LEAVES') -> int:
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
    return int(heightmap[positionRelativeToWorldSlice.x, positionRelativeToWorldSlice.y])


def getSurfacePositionAt(pos: ivec3 | ivec2, heightmapType: str = 'MOTION_BLOCKING_NO_LEAVES') -> ivec3:
    if isinstance(pos, ivec3):
        pos = ivec2(pos.x, pos.z)
    return ivec3(
        pos.x,
        getHeightAt(pos=pos, heightmapType=heightmapType),
        pos.y
    )


def getRandomSurfacePosition(rng=np.random.default_rng(), heightmapType: str = 'MOTION_BLOCKING_NO_LEAVES') -> ivec3:
    startPosition = ivec3(
        globals.buildarea.offset.x + rng.choice(globals.buildarea.size.x),
        0,
        globals.buildarea.offset.y + rng.choice(globals.buildarea.size.y)
    )
    startPosition.y = getHeightAt(startPosition, heightmapType=heightmapType)
    return startPosition
