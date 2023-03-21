from pathlib import Path
from StructureFile import StructureFile


class StructureFolder:

    def __init__(self,
                 structureFolder: Path,
                 structureName: str
                 ):

        self.structureName = structureName

        self.structureFile = StructureFile(structureFolder / structureName)

        self.transitionStructureFiles = dict()
        for connectorStructureFile in structureFolder.glob('connectors/*'):
            if connectorStructureFile.is_file() and connectorStructureFile.name.endswith('.nbt'):
                self.transitionStructureFiles[connectorStructureFile.name] = StructureFile(connectorStructureFile)

        self.decorationStructureFiles = dict()
        for decorationStructionFile in structureFolder.glob('decorations/*'):
            if decorationStructionFile.is_file() and decorationStructionFile.name.endswith('.nbt'):
                self.decorationStructureFiles[decorationStructionFile.name] = StructureFile(decorationStructionFile)
