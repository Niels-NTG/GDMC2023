from pathlib import Path

from gdpc.gdpc import interface
from gdpc.gdpc import Editor
from StructureFolder import StructureFolder

global structureFolders

global buildarea
global editor

global nodeList

# DEBUG
global structureCount
global maxStructureCount


def initialize():
    global structureFolders
    structureFolders = dict()
    loadStructureFiles()

    global buildarea
    buildarea = interface.getBuildArea().toRect()
    global editor
    editor = Editor(multithreading=True, multithreadingWorkers=4)
    editor.loadWorldSlice(rect=buildarea)

    global nodeList
    nodeList = []

    # DEBUG
    global structureCount
    structureCount = 0
    global maxStructureCount
    maxStructureCount = 1200


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
