from pathlib import Path

import glm

from gdpc.gdpc import interface
from gdpc.gdpc import Editor
from gdpc.gdpc.vector_tools import Rect
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
    maxBuildAreaSize = 656
    buildarea = interface.getBuildArea().toRect()
    buildarea = buildarea.centeredSubRect(glm.min(buildarea.size, glm.ivec2(maxBuildAreaSize, maxBuildAreaSize)))
    global editor
    editor = Editor()
    editor.loadWorldSlice(rect=buildarea, cache=True)

    global nodeList
    nodeList = set()


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
