import nbtlib
from glm import ivec3
import numpy as np


def SnbttoNbt(snbt: str) -> nbtlib.Compound:
    return nbtlib.parse_nbt(snbt)


def extractEntityBlockPos(compound: nbtlib.Compound) -> ivec3:
    return ivec3(
        np.floor(compound.get('Pos').get(0)),
        np.floor(compound.get('Pos').get(1)),
        np.floor(compound.get('Pos').get(2))
    )


def extractEntityId(compound: nbtlib.Compound) -> str:
    return compound.get('id')
