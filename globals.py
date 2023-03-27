from pathlib import Path

from gdpc.gdpc import interface
from StructureFolder import StructureFolder

global buildarea
global structureFolders

# DEBUG
global structureCount
global maxStructureCount


def initialize():
    global structureFolders
    structureFolders = dict()
    loadStructureFiles()
    global buildarea
    buildarea = interface.getBuildArea()

    # DEBUG
    global structureCount
    structureCount = 0
    global maxStructureCount
    maxStructureCount = 32


def loadStructureFiles():
    namespace = 'debug'
    for structureFolder in Path('.').glob(f'structures/{namespace}/*/'):
        if structureFolder.is_dir():
            structureName = structureFolder.name
            structureFolders[structureName] = StructureFolder(
                structureFolder=structureFolder,
                name=structureName,
                namespace=namespace
            )
