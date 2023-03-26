import numpy as np

from gdpc.gdpc.vector_tools import Box
from glm import ivec3


def getNextPosition(facing: int = 0, currentBox: Box = None, nextBox: Box = None) -> ivec3:
    if currentBox is None:
        # noinspection PyTypeChecker
        currentBox = Box(ivec3(0, 0, 0), ivec3(0, 0, 0))
    if nextBox is None:
        # noinspection PyTypeChecker
        nextBox = Box(ivec3(0, 0, 0), ivec3(0, 0, 0))
    if facing == 0:
        return currentBox.translated(
            ivec3(
                currentBox.size.x,
                nextBox.offset.y,
                (currentBox.size.z - nextBox.size.z) // 2
            )
        ).offset
    if facing == 1:
        return currentBox.translated(
            ivec3(
                (currentBox.size.x - nextBox.size.x) // 2,
                nextBox.offset.y,
                currentBox.size.z
            )
        ).offset
    if facing == 2:
        return currentBox.translated(
            ivec3(
                -nextBox.size.x,
                nextBox.offset.y,
                (currentBox.size.z - nextBox.size.z) // 2
            )
        ).offset
    if facing == 3:
        return currentBox.translated(
            ivec3(
                (currentBox.size.x - nextBox.size.x) // 2,
                nextBox.offset.y,
                -nextBox.size.z
            )
        ).offset


def rotatePointAroundOrigin(origin: ivec3 = ivec3(0, 0, 0), point: ivec3 = ivec3(0, 0, 0), rotation: int = 0) -> ivec3:
    if rotation == 0:
        return point
    angle = np.deg2rad(rotation * 90)
    return ivec3(
        int(np.round(np.cos(angle) * (point.x - origin.x) - np.sin(angle) * (point.z - origin.z) + origin.x)),
        point.y,
        int(np.round(np.sin(angle) * (point.x - origin.x) + np.cos(angle) * (point.z - origin.z) + origin.z))
    )
