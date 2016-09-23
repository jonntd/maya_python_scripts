from PyQt4.QtGui import *
from PyQt4.QtCore import *


# -----------------------------------------------------------------------------
# Widget Items
# -----------------------------------------------------------------------------
class BaseWidgetClass:
    """Base Class for all Widget items. Store object data, set colors and etc."""
    def __init__(self):
        self.itemIsMovable = False
        self.itemType = ''
        self.currentColor = QColor(Qt.green)
        self.selectedColor = QColor(Qt.white)

    # -------------------------------------------------------------------------
    def setRect(self, size, pos):
        self.setGeometry(QRect(pos.x(), pos.y(), size.width(), size.height()))

    # -------------------------------------------------------------------------
    def setMovable(self, state):
        self.itemIsMovable = state

    # -------------------------------------------------------------------------
    def setType(self, name):
        self.itemType = name

    # -------------------------------------------------------------------------
    def getType(self):
        return self.itemType

    # -------------------------------------------------------------------------
    def setColor(self, newColor):
        self.currentColor = QColor(newColor)
        self.selectedColor = QColor(Qt.white)
        self.setStyleSheet('background-color: ' + self.currentColor.name() + '; color: black;')

    # -------------------------------------------------------------------------
    def getColor(self):
        return str(self.currentColor.name())

    # -------------------------------------------------------------------------
    def selectionColor(self, isSelected):
        if isSelected:
            self.setStyleSheet('background-color: ' + self.selectedColor.name() + '; color: black;')
        else:
            self.setStyleSheet('background-color: ' + self.currentColor.name() + '; color: black;')


# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
class DragButton(QPushButton, BaseWidgetClass):
    """Class based on QPushButton to create movable button with my own functionality"""
    def __init__(self, name):
        super(QPushButton, self).__init__(name)
        self.__mousePressPos = None
        self.__mouseMovePos = None
        self.connectedObjects = None
        self.state = False

    # -------------------------------------------------------------------------
    def mousePressEvent(self, event):
        self.__mousePressPos = None
        self.__mouseMovePos = None
        if event.button() == Qt.LeftButton:
            self.__mousePressPos = event.globalPos()
            self.__mouseMovePos = event.globalPos()
        super(DragButton, self).mousePressEvent(event)

    # -------------------------------------------------------------------------
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.itemIsMovable:
            currPos = self.mapToGlobal(self.pos())
            globalPos = event.globalPos()
            diff = globalPos - self.__mouseMovePos
            newPos = self.mapFromGlobal(currPos + diff)
            self.move(newPos)
            self.__mouseMovePos = globalPos
        super(DragButton, self).mouseMoveEvent(event)

    # -------------------------------------------------------------------------
    def mouseReleaseEvent(self, event):
        if self.__mousePressPos is not None:
            moved = event.globalPos() - self.__mousePressPos
            if moved.manhattanLength() > 3:
                event.ignore()
                return
        super(DragButton, self).mouseReleaseEvent(event)

    # -------------------------------------------------------------------------
    def setObjs(self, objs):
        self.connectedObjects = objs
        self.state = False

    # -------------------------------------------------------------------------
    def getObjs(self):
        data = [x[0]+x[1] for x in self.connectedObjects]
        return data

    # -------------------------------------------------------------------------
    def getRawObjs(self):
        return self.connectedObjects


# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
class DragCheckBox(QCheckBox, BaseWidgetClass):
    """Class based on QCheckBox to create movable checkbox with my own functionality"""
    def __init__(self, name):
        super(QCheckBox, self).__init__(name)
        self.__mousePressPos = None
        self.__mouseMovePos = None
        self.checkedAttr = None

    # -------------------------------------------------------------------------
    def mousePressEvent(self, event):
        self.__mousePressPos = None
        self.__mouseMovePos = None
        if event.button() == Qt.LeftButton:
            self.__mousePressPos = event.globalPos()
            self.__mouseMovePos = event.globalPos()
        super(DragCheckBox, self).mousePressEvent(event)

    # -------------------------------------------------------------------------
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.itemIsMovable:
            currPos = self.mapToGlobal(self.pos())
            globalPos = event.globalPos()
            diff = globalPos - self.__mouseMovePos
            newPos = self.mapFromGlobal(currPos + diff)
            self.move(newPos)
            self.__mouseMovePos = globalPos
        super(DragCheckBox, self).mouseMoveEvent(event)

    # -------------------------------------------------------------------------
    def mouseReleaseEvent(self, event):
        if self.__mousePressPos is not None:
            moved = event.globalPos() - self.__mousePressPos
            if moved.manhattanLength() > 3:
                event.ignore()
                return
        super(DragCheckBox, self).mouseReleaseEvent(event)

    # -------------------------------------------------------------------------
    def setObjs(self, attr):
        self.checkedAttr = attr

    # -------------------------------------------------------------------------
    def getObjs(self):
        data = self.checkedAttr[0] + self.checkedAttr[1] + '.' + self.checkedAttr[2]
        return data

    # -------------------------------------------------------------------------
    def getRawObjs(self):
        return self.checkedAttr
