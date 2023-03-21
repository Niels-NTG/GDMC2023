from pathlib import Path
from nbt import nbt
import numpy as np


class StructureFile:

    def __init__(self,
                 filePath: Path):
        filePath = filePath.with_suffix('.nbt')
        self.nbt = nbt.NBTFile(filename=filePath)
        with open(filePath, 'rb') as file:
            self.file = file.read()

    def getBlockAt(self, x, y, z):
        for block in self.nbt['blocks']:
            if block["pos"][0].value == x and block["pos"][1].value == y and block["pos"][2].value == z:
                return block

    def getBlockMaterial(self, block):
        return self.nbt["palette"][block["state"].value]['Name'].value

    def getBlockMaterialAt(self, x, y, z):
        return self.getBlockMaterial(self.getBlockAt(x, y, z))

    # Get block properties (also known as block states: https://minecraft.fandom.com/wiki/Block_states) of a block.
    # This may contain information on the orientation of a block or open or closed stated of a door.
    def getBlockProperties(self, block):
        properties = dict()
        if "Properties" in self.nbt["palette"][block["state"].value].keys():
            for key in self.nbt["palette"][block["state"].value]["Properties"].keys():
                properties[key] = self.nbt["palette"][block["state"].value]["Properties"][key].value
        return properties

    def getBlockPropertiesAt(self, x, y, z):
        return self.getBlockProperties(self.getBlockAt(x, y, z))

    def getSizeX(self):
        return self.nbt["size"][0].value

    def getSizeY(self):
        return self.nbt["size"][1].value

    def getSizeZ(self):
        return self.nbt["size"][2].value

    def getShortestDimension(self):
        return np.argmin([np.abs(self.getSizeX()), np.abs(self.getSizeY()), np.abs(self.getSizeZ())])

    def getLongestDimension(self):
        return np.argmax([np.abs(self.getSizeX()), np.abs(self.getSizeY()), np.abs(self.getSizeZ())])

    def getShortestHorizontalDimension(self):
        return np.argmin([np.abs(self.getSizeX()), np.abs(self.getSizeZ())]) * 2

    def getLongestHorizontalDimension(self):
        return np.argmax([np.abs(self.getSizeX()), np.abs(self.getSizeZ())]) * 2

    def getShortestSize(self):
        return [self.getSizeX(), self.getSizeY(), self.getSizeZ()][self.getShortestDimension()]

    def getLongestSize(self):
        return [self.getSizeX(), self.getSizeY(), self.getSizeZ()][self.getLongestDimension()]

    def getShortestHorizontalSize(self):
        return [self.getSizeX(), 0, self.getSizeZ()][self.getShortestHorizontalDimension()]

    def getLongestHorizontalSize(self):
        return [self.getSizeX(), 0, self.getSizeZ()][self.getLongestHorizontalDimension()]

    def getCenterPivot(self):
        return [
            int(np.floor(self.getSizeX() / 2)),
            0,
            int(np.floor(self.getSizeZ() / 2))
        ]
