#----------------------------------------------------------------------------------
# Flat window class
# add this line for window function for hide window frame
#      formCollect.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.FramelessWindowHint)
#
# Base class for moove and resize a flat window
#----------------------------------------------------------------------------------
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from studioLibs import functions as sfn

#----------------------------------------------------------------------------------
pluginBasePath = sfn.dirname() + '/'

#----------------------------------------------------------------------------------
class FlatWindow():
    def __init__(self, obj):
        self.workObj = obj
        self.leftClick = False
        self.isResize = False

        self.loadQss()

    #------------------------------------------------------------------------------
    def loadQss(self):
        print(pluginBasePath + 'qss/flatWindow.qss')
        styleF = QFile()
        styleF.setFileName(pluginBasePath + 'qss/flatWindow.qss')
        styleF.open(QFile.ReadOnly)
        qssStr = QString(styleF.readAll())

        self.setStyleSheet(qssStr)


    #------------------------------------------------------------------------------
    def mousePressEvent(self, event):
        super(self.workObj, self).mousePressEvent(event)
        if event.button() == Qt.LeftButton:
            if event.x() > self.width()-20 and event.y() > self.height()-20:
                self.isResize = True
            else:
                self.leftClick = True

            self.clickX = event.x() 
            self.clickY = event.y()


    #------------------------------------------------------------------------------
    def mouseReleaseEvent(self, event):
        super(self.workObj, self).mouseReleaseEvent(event)
        self.leftClick = False
        self.isResize = False


    #------------------------------------------------------------------------------
    def mouseMoveEvent(self, event):
        super(self.workObj, self).mouseMoveEvent(event)

        if self.isResize == True:
            self.resize(QSize(event.x(), event.y()))
            
        if self.leftClick == True:
            self.move(QPoint(event.globalX() - self.clickX, event.globalY() - self.clickY))
