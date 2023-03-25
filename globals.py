from StructureFolder import StructureFolder
from pathlib import Path

global structureFolders


def initialize():
    global structureFolders
    structureFolders = dict()
    loadStructureFiles()


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
