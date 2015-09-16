import os
import sys
import sip
import maya.OpenMayaUI as mui
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import uic
import maya.cmds as cmds
import maya.mel as mel

from studioLibs import FlatWindowClass as flat

from studioLibs import functions as fn
from studioLibs import shotgun as sh
from studioLibs import perforce as pf

from pprint import pprint

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
def getMayaWindow():
    ptr = mui.MQtUtil.mainWindow()
    return sip.wrapinstance(long(ptr), QObject)

#----------------------------------------------------------------------
class PlayblasterFinalWnd(QDialog, flat.FlatWindow):
    def __init__(self, fname, parent=getMayaWindow()):
        super(PlayblasterFinalWnd, self).__init__(parent)
        uic.loadUi('final.ui', self)
        flat.FlatWindow.__init__(self, PlayblasterFinalWnd)

        self.fileName = fname

        # get shotgun user
        self.shotgun = sh.studioShotgun("https://oamedia.shotgunstudio.com",
                                        'maya',
                                        '9e9d3222407460dfbf5383906a5a241b4020d79a25ba8c6b2411787ab6aa3974',
                                        67)

        self.userList = self.shotgun.getAllUsers()
       
        self.userName = 'Unknown'
        self.settings = fn.loadSettings(fileName)
        if 'shotgun' in self.settings:
            self.userName = self.settings['shotgun']
            for name in self.userList:
                if name['name'] == self.userName:
                    self.userName = name['login']
                    self.userId =   name['id']

        self.shotgunCheck.setText('Create Shotgun Version ( ' + self.userName + ' )')

        # get shotgun shot
        curName = self.fileName.split('/')[-2]
        episodeNum = self.fileName.split('/')[2].split('_')[-1]
        self.curShot = self.shotgun.findShotByName('ep'+episodeNum, curName)
        taskNames = [x['name'] for x in self.curShot['tasks']]
        self.tasks = dict([(x['name'],x['id']) for x in self.curShot['tasks']])
        self.shotgunTaskCombo.addItems(taskNames)

        # set perforce
        self.perforce = pf.studioPerforce('', '')

        self.connect(self.perforceCheck, SIGNAL("stateChanged(int)"), self.checkBtnState)
        self.connect(self.shotgunCheck,  SIGNAL("stateChanged(int)"), self.checkBtnState)
        self.connect(self.saveButton,    SIGNAL("released()"),        self.saveButtonClick)


    #------------------------------------------------------------------
    def checkBtnState(self, data):
        if self.perforceCheck.checkState() or self.shotgunCheck.checkState():
            self.saveButton.setEnabled(True)
        else:
            self.saveButton.setEnabled(False)


    #------------------------------------------------------------------
    def saveButtonClick(self):
        task = self.shotgunTaskCombo.currentText()
        taskId = self.tasks[str(task)]
        comm = str(self.commentText.toPlainText())

        if self.perforceCheck.checkState():
            print('----------------------------------------')
            print('export to perforce...')
            print('fileName: ' + self.fileName)
            print('comment: ' + comm)
            self.perforce.submit(self.fileName, comm)

        if self.shotgunCheck.checkState():
            print('----------------------------------------')
            print('export to shotgun')
            print('task: ' + str(task))
            print('fileName: ' + self.fileName)
            print('comment: ' + comm)
            print('taskId: ' + str(taskId))
            print('userId: ' + str(self.userId))

            self.shotgun.createVersion(self.curShot['id'], taskId, self.userId, self.fileName, comm)

        print('----------------------------------------')
        self.accept()

#----------------------------------------------------------------------
# MAIN
#----------------------------------------------------------------------
def wnd(fname):
    wnd = PlayblasterFinalWnd(fname)
    wnd.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
    wnd.show()

#wnd()
