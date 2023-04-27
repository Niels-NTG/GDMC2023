import functools

import numpy as np

from gdpc.gdpc.vector_tools import Box
from glm import ivec3


@functools.cache
def getNextPosition(facing: int = 0, currentBox: Box = None, nextBox: Box = None) -> ivec3:
    if currentBox is None:
        currentBox = Box()
    if nextBox is None:
        nextBox = Box()

    currentCenter = ivec3(currentBox.center.x, currentBox.offset.y, currentBox.center.z)
    nextCenter = ivec3(currentBox.size.x + nextBox.center.x, nextBox.offset.y, currentCenter.z)
    nextPoint = rotatePointAroundOrigin(
        origin=currentCenter,
        point=nextCenter,
        rotation=facing
    )
    nextPoint = nextPoint - ivec3(nextBox.middle.x, 0, nextBox.middle.z)
    return nextPoint


@functools.cache
def rotatePointAroundOrigin(origin: ivec3 = ivec3(0, 0, 0), point: ivec3 = ivec3(0, 0, 0), rotation: int = 0) -> ivec3:
    if rotation == 0:
        return point
    angle = np.deg2rad(rotation * 90)
    return ivec3(
        int(np.round(np.cos(angle) * (point.x - origin.x) - np.sin(angle) * (point.z - origin.z) + origin.x)),
        point.y,
        int(np.round(np.sin(angle) * (point.x - origin.x) + np.cos(angle) * (point.z - origin.z) + origin.z))
    )
