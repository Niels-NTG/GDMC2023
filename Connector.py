from glm import ivec3


class Connector:

    facing: int
    offset: ivec3
    nextStructure: list[str]

    def __init__(
        self,
        facing: int = 0,
        offset: ivec3 = ivec3(0, 0, 0),
        nextStructure: list[str] = None,
    ):
        self.facing = facing % 4
        self.offset = offset
        self.nextStructure = [] if nextStructure is None else nextStructure

    def __hash__(self):
        # TODO implement connectors that mirrors the vertical axis (for connecting structures on top of each other)
        # return hash((self.facing, self.offset))
        # return hash(self.facing)
        # TODO do not hash for debugging purposes
        return self.facing

    def __eq__(self, other):
        return hash(self) == hash(other)
