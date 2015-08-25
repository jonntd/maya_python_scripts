import json
import os

#----------------------------------------------------------------------
def saveSettings(data, fileName):
    ''' save input 'data' to file with 'fileName' and replace all data in file '''
    outData = json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))

    fp = open(fileName, 'w')
    fp.write(outData)
    fp.close()

#----------------------------------------------------------------------
def loadSettings(fileName):
    ''' read file with 'fileName' and parse data '''
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
    ''' read file, parse it and union with input data, save result and return it '''
    inData = loadSettings(fileName)
    inData.update(data)
    saveSettings(inData, fileName)

    return inData

#----------------------------------------------------------------------
# tests
'''
fileName = 'C:/Users/m.kuzubov/Documents/maya/2014-x64/scripts/settings.txt'

data = {'a':[1,2,3], 'c':12}
saveSettings(data, fileName)

a = {'a':1, 'b':2}
b = {'c':3, 'd':4}
c = {'a':5, 'd':6}

print(updateSettings(b, fileName))
'''
