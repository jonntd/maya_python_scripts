import os
import sys
import sip
import maya.OpenMayaUI as mui
from PyQt4.QtCore import *
import maya.cmds as cmds
import json


# -----------------------------------------------------------------------------
def getMayaWindow():
    ptr = mui.MQtUtil.mainWindow()
    return sip.wrapinstance(long(ptr), QObject)


# -----------------------------------------------------------------------------
def dirname():
    encoding = sys.getfilesystemencoding()
    path = os.path.dirname(unicode(os.path.abspath(__file__), encoding)).replace('\\', '/')
    os.chdir(path)
    return path


# -----------------------------------------------------------------------------
# SAVE and LOAD data
# -----------------------------------------------------------------------------
def saveSettings(data, fileName):
    """ save input 'data' to file with 'fileName' and replace all data in file """
    outData = json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))

    fp = open(fileName, 'wb')
    fp.write(outData)
    fp.close()


# -----------------------------------------------------------------------------
def loadSettings(fileName):
    """ read file with 'fileName' and parse data """
    if os.path.isfile(fileName):
        fp = open(fileName, 'rb')
        inData = fp.read()
        fp.close()

        return json.loads(inData)
    else:
        return {}


# -----------------------------------------------------------------------------
# store data in maya 'network' node
# -----------------------------------------------------------------------------
def storeData(nodeName, attr, data, attrType):
    storeNode = cmds.ls(nodeName)
    if not storeNode:
        storeNode = cmds.createNode('network', name=nodeName)
    else:
        storeNode = storeNode[0]

    if attrType == 'string':
        if attr not in cmds.listAttr(storeNode):
            cmds.addAttr(storeNode, dt='string', ln=attr)
        cmds.setAttr(storeNode + '.' + attr, data, type='string')
    elif attrType == 'float':
        if attr not in cmds.listAttr(storeNode):
            cmds.addAttr(storeNode, at='float', ln=attr)
        cmds.setAttr(storeNode + '.' + attr, data)


# -----------------------------------------------------------------------------
def takeData(nodeName, attr):
    storeNode = cmds.ls(nodeName)
    if not storeNode:
        return []

    if attr in cmds.listAttr(storeNode[0]):
        return cmds.getAttr(storeNode[0] + '.' + attr)


# -----------------------------------------------------------------------------
def takeAllData(nodeName):
    storeNode = cmds.ls(nodeName)
    if not storeNode:
        return []
    data = cmds.listAttr(storeNode[0], ud=True)
    if data is None:
        return []
    else:
        return data


# -----------------------------------------------------------------------------
def deleteData(nodeName, attr):
    storeNode = cmds.ls(nodeName)
    if storeNode:
        if attr in cmds.listAttr(storeNode[0]):
            cmds.deleteAttr(storeNode[0] + '.' + attr)    
