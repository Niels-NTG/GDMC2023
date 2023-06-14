from __future__ import annotations

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from Node import Node

from glm import ivec3

from StructureFile import StructureFile


class Connector:

    facing: int
    offset: ivec3
    nextStructure: list[str]
    transitionStructure: StructureFile | None

    _finalNode: Node | None

    def __init__(
        self,
        facing: int = 0,
        offset: ivec3 = ivec3(0, 0, 0),
        nextStructure: list[str] = None,
        transitionStructure: StructureFile = None,
    ):
        self.facing = facing % 4
        self.offset = offset
        self.nextStructure = [] if nextStructure is None else nextStructure
        self.transitionStructure = transitionStructure

        self.finalNode = None

    @property
    def finalNode(self) -> Node | None:
        return self._finalNode

    @finalNode.setter
    def finalNode(self, node: Node):
        self._finalNode = node

    def __hash__(self):
        # TODO implement connectors that mirrors the vertical axis (for connecting structures on top of each other)
        return hash((self.facing, self.offset))

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __repr__(self):
        return f'{__class__.__name__}; f: {self.facing}; offset: {self.offset}; finalNode: {self.finalNode}'
