import sip
import maya.OpenMayaUI as mui
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import uic

def getMayaWindow():
    ptr = mui.MQtUtil.mainWindow()
    return sip.wrapinstance(long(ptr), QObject)

class MyDialog(QDialog):
    def __init__(self, parent=getMayaWindow()):
        super(MyDialog, self).__init__(parent)
        uic.loadUi('test_qt5.ui', self)

        self.connect(self.spinbox, SIGNAL("valueChanged(int)"), self.log_to_console)
        self.connect(self.button,  SIGNAL("released()"),        self.push_me)

    def log_to_console(self,i):
        print i

    def push_me(self):
        print('push me button')


def myWnd():
    wnd = MyDialog()
    wnd.show()

myWnd()
