import functools
from typing import Iterator

import numpy as np
import glm
from glm import ivec3, ivec2

from gdpc.gdpc.vector_tools import Box, Rect


@functools.cache
def getNextPosition(
    facing: int = 0,
    currentBox: Box = None,
    nextBox: Box = None,
    offset: ivec3 = ivec3(0, 0, 0)
) -> ivec3:
    if currentBox is None:
        currentBox = Box()
    if nextBox is None:
        nextBox = Box()

    currentCenter = ivec3(currentBox.center.x, currentBox.offset.y, currentBox.center.z)
    nextCenter = ivec3(currentBox.size.x + nextBox.center.x, nextBox.offset.y, currentCenter.z) + offset
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
        rectB.end.x <= rectA.last.x and
        rectB.end.y <= rectA.last.y
    )


@functools.cache
def addVec2ToVec3(a: ivec2 = ivec2(0, 0), b: ivec2 = ivec2(0, 0), y: int = 0) -> ivec3:
    return ivec3(a.x + b.x, y, a.y + b.y)


@functools.cache
def loop2DwithStride(
    begin: ivec2 = ivec2(0, 0),
    end: ivec2 = ivec2(0, 0),
    stride: ivec2 | int = ivec2(1, 1)
) -> Iterator[ivec2]:
    if isinstance(stride, int):
        stride = ivec2(1, 1) * stride
    for x in range(begin.x, end.x, stride.x):
        for y in range(begin.y, end.y, stride.y):
            yield ivec2(x, y)


@functools.cache
def loop2DwithRects(
    begin: ivec2 = ivec2(0, 0),
    end: ivec2 = ivec2(0, 0),
    stride: ivec2 = ivec2(1, 1)
) -> Iterator[Rect]:
    for x in range(begin.x, end.x, stride.x):
        for y in range(begin.y, end.y, stride.y):
            newRectOffset = ivec2(x, y)
            newRectSize = stride
            # noinspection PyTypeChecker
            newRect = Rect(
                offset=newRectOffset,
                size=newRectSize
            )
            newRect.end = glm.min(newRect.end, end)
            yield newRect


def mergeRects(
    rectList: list[Rect],
) -> Rect:
    if len(rectList) == 1:
        return rectList[0]
    rectStarts: list[ivec2] = []
    rectEnds: list[ivec2] = []
    for rect in rectList:
        rectStarts.append(rect.begin)
        rectEnds.append(rect.end)
    # noinspection PyTypeChecker
    rect = Rect(
        offset=glm.min(rectStarts),
    )
    rect.end = glm.max(rectEnds)
    return rect
