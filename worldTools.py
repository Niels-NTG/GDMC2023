from glm import ivec2, ivec3

import globals
from StructureBase import Structure
from gdpc.gdpc.vector_tools import Box


def isStructureInsideBuildArea(structure: Structure):
    return isBoxInsideBuildArea(structure.boxInWorldSpace)


def isBoxInsideBuildArea(box: Box):
    return box.toRect().collides(globals.buildarea)


def getHeightAt(pos: ivec3 | ivec2, heightmapType: str = 'MOTION_BLOCKING_NO_LEAVES'):
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

    positionRelativeToWorldSlice = pos - globals.editor.worldSlice.rect.offset
    return heightmap[positionRelativeToWorldSlice.x, positionRelativeToWorldSlice.y]
