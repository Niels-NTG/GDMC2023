from StructureFolder import StructureFolder
from pathlib import Path

global structureFiles


def initialize():
    global structureFiles
    structureFiles = dict()
    loadStructureFiles()


def loadStructureFiles():
    for structureFolder in Path('.').glob('structures/debug/*/'):
        if structureFolder.is_dir():
            structureFileName = structureFolder.name
            structureFiles[structureFileName] = StructureFolder(
                structureFolder=structureFolder,
                structureName=structureFileName
            )
