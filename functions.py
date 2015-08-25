import os
import sys
import json
import shutil

#----------------------------------------------------------------------
def saveSettings(data, fileName):
    """ save input "data" to file with "fileName" and replace all data in file """
    outData = json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))

    fp = open(fileName, 'w')
    fp.write(outData)
    fp.close()


#----------------------------------------------------------------------
def loadSettings(fileName):
    """ read file with 'fileName' and parse data """
    if os.path.isfile(fileName):
        fp = open(fileName, 'r')
        inData = fp.read()
        fp.close()

        data = json.loads(inData)
        return data
    else:
        return {}


#----------------------------------------------------------------------
def updateSettings(data, fileName):
    """ read file, parse it and union with input data, save result and return it """
    inData = loadSettings(fileName)
    inData.update(data)
    saveSettings(inData, fileName)

    return inData


#----------------------------------------------------------------------
def setRecentFiles(fileName, userFile):
    """ save custom recent files in user file """
    oldFiles = getRecentFiles(userFile)

    if fileName not in oldFiles:
        if len(oldFiles) > 9:
            oldFiles.pop(0)
        oldFiles.append(fileName)
        fileopen = open(userFile, "w+")

        for x in oldFiles:
            fileopen.write(x + '\n')

        fileopen.close()


#----------------------------------------------------------------------
def getRecentFiles(userFile):
    """ read custom recent files from user file """
    param = []

    if os.path.isfile(userFile):
        fileopen = open(userFile, "r+")
        param = fileopen.read().splitlines()

        fileopen.close()

    return param


#----------------------------------------------------------------------
def dirname():
    encoding = sys.getfilesystemencoding()
    path = os.path.dirname(unicode(os.path.abspath(__file__), encoding)).replace('\\', '/')
    os.chdir(path)
    return path
