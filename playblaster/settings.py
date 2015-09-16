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
class PlayblasterSettingsWnd(QDialog, flat.FlatWindow):
    def __init__(self, parent=getMayaWindow()):
        super(PlayblasterSettingsWnd, self).__init__(parent)
        flat.FlatWindow.__init__(self, PlayblasterSettingsWnd)
        uic.loadUi('settings.ui', self)

        self.settings = fn.loadSettings(fileName)
        if 'display' in self.settings:
            self.displayUserEdit.setText(self.settings['display'])

        # get shotgun user
        self.shotgun = sh.studioShotgun("https://oamedia.shotgunstudio.com",
                                        'maya',
                                        '9e9d3222407460dfbf5383906a5a241b4020d79a25ba8c6b2411787ab6aa3974',
                                        67)

        self.userList = self.shotgun.getAllUsers()
        self.userList = [x['name'] for x in self.userList]
        self.userList.sort()
        if self.userList:
            self.shotgunUserCombo.addItems(self.userList)

        if 'shotgun' in self.settings:
            if self.settings['shotgun'] in self.userList:
                num = self.userList.index(self.settings['shotgun'])
                self.shotgunUserCombo.setCurrentIndex(num)

        
        self.connect(self.saveButton, SIGNAL("released()"), self.saveButtonClick)

    def saveButtonClick(self):
        self.settings['shotgun'] = str(self.shotgunUserCombo.currentText())
        self.settings['display'] = str(self.displayUserEdit.text())
        fn.saveSettings(self.settings, fileName)
        self.accept()

#----------------------------------------------------------------------
# MAIN
#----------------------------------------------------------------------
def wnd():
    wnd = PlayblasterSettingsWnd()
    wnd.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
    wnd.show()

#playblasterSettings()
