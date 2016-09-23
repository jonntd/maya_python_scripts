from PyQt4.QtCore import *


class FlatWindow:
    """Flat Window class"""
    def __init__(self, obj):
        self.__workObj = obj
        self.__leftClick = False
        self.__isResize = False
        self.__clickX = 0
        self.__clickY = 0

    # -------------------------------------------------------------------------
    def mousePressEvent(self, event):
        super(self.__workObj, self).mousePressEvent(event)
        if event.button() == Qt.LeftButton:
            if event.x() > self.width()-20 and event.y() > self.height()-20:
                self.__isResize = True
            else:
                self.__leftClick = True

            self.__clickX = event.x()
            self.__clickY = event.y()

    # -------------------------------------------------------------------------
    def mouseReleaseEvent(self, event):
        super(self.__workObj, self).mouseReleaseEvent(event)
        self.__leftClick = False
        self.__isResize = False

    # -------------------------------------------------------------------------
    def mouseMoveEvent(self, event):
        super(self.__workObj, self).mouseMoveEvent(event)

        if self.__isResize:
            self.resize(QSize(event.x(), event.y()))
            
        if self.__leftClick:
            self.move(QPoint(event.globalX() - self.__clickX, event.globalY() - self.__clickY))
