import os
import sys
import time
import maya.cmds as cmds

from studioLibs import functions as fn

import final

#----------------------------------------------------------------------
def dirname():
    encoding = sys.getfilesystemencoding()
    path = os.path.dirname(unicode(os.path.abspath(__file__), encoding)).replace('\\', '/')
    os.chdir(path)
    return path
    
curPath = dirname()
os.chdir(curPath)
fileName = os.path.join(curPath, '_settings.data')

#----------------------------------------------------------------------
class PlayBlaster():
    def __init__(self, resolution=[1920, 1080, 1.0], range=[]):
        self.userName = 'Max'
        self.resolution = resolution
        self.curPanel = cmds.getPanel(wf=True)

        self.userName = 'Unknown'
        self.settings = fn.loadSettings(fileName)
        if 'display' in self.settings:
            self.userName = self.settings['display']

        curDate = time.localtime()
        self.curTime = '%02d:%02d %02d.%02d.%04d' % (curDate.tm_hour, curDate.tm_min, curDate.tm_mday, curDate.tm_mon, curDate.tm_year)

        if range:
            self.range = range
        else:
            self.range = [cmds.playbackOptions(q=True, min=True), cmds.playbackOptions(q=True, max=True)]
        self.duration = int(self.range[1] - self.range[0] + 1)

        self.getFileName()
        self.getFPS()

    #-----------------------------------------------------------------
    def getFileName(self):
        fullName = cmds.file(q=True, sn=True)
        if fullName:
            self.fileName = '.'.join(os.path.basename(fullName).split('.')[:-1]) + '_playblast.mov'
            self.pathName = os.path.dirname(fullName)
        else:
            self.fileName = 'test.mov'
            self.pathName = 'd:/temp/'

    #-----------------------------------------------------------------
    def getFPS(self):
        data = { 'game':15, 'film':24, 'pal':25, 'ntsc':30, 'show':48, 'palf':50, 'ntscf':60 }
        qFPS = cmds.currentUnit( query=True, t=True )
        self.curFPS = data[qFPS] if qFPS in data else 0

    #-----------------------------------------------------------------
    def setRenderGlobals(self):
        cmds.setAttr ("defaultResolution.width", self.resolution[0])
        cmds.setAttr ("defaultResolution.height", self.resolution[1])
        cmds.setAttr ("defaultResolution.pixelAspect", self.resolution[2])

    #-----------------------------------------------------------------
    def setDisplay(self):
        cmds.modelEditor(self.curPanel, e=True, 
                         displayAppearance='smoothShaded', 
                         displayTextures=True,
                         allObjects=False,
                         polymeshes=True,
                         locators=False,
                         grid=False,
                         manipulators=False,
                         hud=True)

        cam = cmds.modelEditor(self.curPanel, q=True, camera=True)
        cmds.camera(cam, e=True, dr=1, dfg=0, dsa=0, ovr=1.2)

    #-----------------------------------------------------------------
    def restoreViewportParams(self):
        cmds.modelEditor(self.curPanel, e=True, 
                         locators=True,
                         grid=True,
                         manipulators=True,
                         nurbsCurves=True)

    #-----------------------------------------------------------------
    def delHUD(self):
        for i in range(10):
            cmds.headsUpDisplay (rp=[i,0])

    #-----------------------------------------------------------------
    def setHUD(self):
        self.delHUD()

        cmds.headsUpDisplay( 'HUDObjectSceneName', section=0, block=0, blockSize='large', label='Scene:  ' + self.fileName,         dfs='large', labelFontSize='large')
        cmds.headsUpDisplay( 'HUDUserName',        section=2, block=0, blockSize='large', label='User Name:  ' + self.userName,     dfs='large', labelFontSize='large')
        cmds.headsUpDisplay( 'HUDDate',            section=4, block=0, blockSize='large', label='Date:  ' + self.curTime,           dfs='large', labelFontSize='large')
        cmds.headsUpDisplay( 'HUDFPS',             section=5, block=0, blockSize='large', label='FPS:  ' + str(self.curFPS),        dfs='large', labelFontSize='large')
        cmds.headsUpDisplay( 'HUDDuration',        section=7, block=0, blockSize='large', label='Duration:  ' + str(self.duration), dfs='large', labelFontSize='large')
        cmds.headsUpDisplay( 'HUDCurentFrame',     section=9, block=0, blockSize='large', label='Current Frame: ', dfs='large', labelFontSize='large', command = lambda: cmds.currentTime(query=True), atr=True)

    #-----------------------------------------------------------------
    def start(self):
        self.setRenderGlobals()
        self.setDisplay()
        self.setHUD()

        fname = self.pathName + '/' + self.fileName

        cmds.playblast(filename=fname,
                       fo=True, fp=4, orn=True, 
                       wh = (960, 540), 
                       format='qt', percent=100, compression='H.264', quality=100, 
                       st=self.range[0], et=self.range[1])

        self.delHUD()

        return fname


#----------------------------------------------------------------------
def playblast():
    blast = PlayBlaster()
    fname = blast.start()
    print('fname', fname)
    final.wnd(fname)

#playblast()



