from pathlib import Path

from gdpc.gdpc import interface
from gdpc.gdpc import Editor
from StructureFolder import StructureFolder

global structureFolders

global buildarea
global editor

global nodeList


def initialize():
    global structureFolders
    structureFolders = dict()
    loadStructureFiles()

    global buildarea
    buildarea = interface.getBuildArea().toRect()
    global editor
    editor = Editor()
    editor.loadWorldSlice(rect=buildarea, cache=True)

    global nodeList
    nodeList = []


def loadStructureFiles():
    namespace = 'gamma'
    for structureFolder in Path('.').glob(f'structures/{namespace}/*/'):
        if structureFolder.is_dir():
            structureName = structureFolder.name
            structureFolders[structureName] = StructureFolder(
                structureFolder=structureFolder,
                name=structureName,
                namespace=namespace
            )
