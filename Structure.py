from pathlib import Path
from nbt import nbt


# TODO figure out on how to extend a class in Python. Maybe this:
#  https://www.geeksforgeeks.org/extend-class-method-in-python/ ?
class StructurePrototype:

    def __init__(self):
        # TODO get folder name, use that as the NBT file to load.
        nbtLocation = Path(__file__).resolve().parent / Path(__file__).resolve().name

        self.nbt = nbt.NBTFile(Path(nbtLocation).with_suffix('.nbt'), 'rb')

    def getConnectors(self):
        pass

    def getPreProcessingSteps(self):
        pass

    def getPostProcessingSteps(self):
        pass
