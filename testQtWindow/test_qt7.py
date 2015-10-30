import sip
import maya.OpenMayaUI as mui
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import uic

from studioLibs import FlatWindowClass as flat

def getMayaWindow():
    ptr = mui.MQtUtil.mainWindow()
    return sip.wrapinstance(long(ptr), QObject)

class MyDialog(QDialog, flat.FlatWindow):
    def __init__(self, parent=getMayaWindow()):
        super(MyDialog, self).__init__(parent)
        flat.FlatWindow.__init__(self, MyDialog)
        uic.loadUi('test_qt7.ui', self)

        self.connect(self.spinbox, SIGNAL("valueChanged(int)"), self.log_to_console)
        self.connect(self.button,  SIGNAL("released()"),        self.push_me)

    def log_to_console(self,i):
        print i

    def push_me(self):
        print('push me button')


def myWnd():
    wnd = MyDialog()
    wnd.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
    wnd.show()

myWnd()
