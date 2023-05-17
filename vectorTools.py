import functools

import numpy as np
from glm import ivec3, ivec2

from gdpc.gdpc.vector_tools import Box, Rect


@functools.cache
def getNextPosition(facing: int = 0, currentBox: Box = None, nextBox: Box = None) -> ivec3:
    if currentBox is None:
        currentBox = Box()
    if nextBox is None:
        nextBox = Box()

    currentCenter = ivec3(currentBox.center.x, currentBox.offset.y, currentBox.center.z)
    nextCenter = ivec3(currentBox.size.x + nextBox.center.x, nextBox.offset.y, currentCenter.z)
    nextPoint = rotatePointAroundOrigin3D(
        origin=currentCenter,
        point=nextCenter,
        rotation=facing
    )
    nextPoint = nextPoint - ivec3(nextBox.middle.x, 0, nextBox.middle.z)
    return nextPoint


@functools.cache
def rotatePointAroundOrigin3D(
    origin: ivec3 = ivec3(0, 0, 0),
    point: ivec3 = ivec3(0, 0, 0),
    rotation: int = 0
) -> ivec3:
    if rotation == 0:
        return point
    angle = np.deg2rad(rotation * 90)
    return ivec3(
        int(np.round(np.cos(angle) * (point.x - origin.x) - np.sin(angle) * (point.z - origin.z) + origin.x)),
        point.y,
        int(np.round(np.sin(angle) * (point.x - origin.x) + np.cos(angle) * (point.z - origin.z) + origin.z))
    )


@functools.cache
def rotatePointAroundOrigin2D(
    origin: ivec2 = ivec3(0, 0, 0),
    point: ivec2 = ivec3(0, 0, 0),
    rotation: int = 0
) -> ivec2:
    if rotation == 0:
        return point
    angle = np.deg2rad(rotation * 90)
    return ivec2(
        int(np.round(np.cos(angle) * (point.x - origin.x) - np.sin(angle) * (point.y - origin.y) + origin.x)),
        int(np.round(np.sin(angle) * (point.x - origin.x) + np.cos(angle) * (point.y - origin.y) + origin.y))
    )


@functools.cache
def isRectinRect(rectA: Rect, rectB: Rect) -> bool:
    return (
        rectB.begin.x >= rectA.begin.x and
        rectB.begin.y >= rectA.begin.y and
        rectB.end.x <= rectA.end.x and
        rectB.end.y <= rectA.end.y
    )


@functools.cache
def addVec2ToVec3(a: ivec2 = ivec2(0, 0), b: ivec2 = ivec2(0, 0), y: int = 0) -> ivec3:
    return ivec3(a.x + b.x, y, a.y + b.y)
