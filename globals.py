from glm import ivec3

from StructureFolder import StructureFolder
from pathlib import Path

global startPosition
global structureFolders
global structureCount
global maxStructureCount


def initialize():
    global structureFolders
    structureFolders = dict()
    loadStructureFiles()
    global startPosition
    # TODO implement getbuildarea
    startPosition = ivec3(423, 0, 166)
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
