from PyQt4.QtGui import *
from PyQt4.QtCore import *


# -----------------------------------------------------------------------------
# Graphics Items
# -----------------------------------------------------------------------------
class BaseObjectClass:
    """Base Class for all Graphics items. Store object data, set colors and etc."""
    def __init__(self, objs):
        self.connectedObjects = objs
        self.selectedColor = Qt.white
        self.currentColor = Qt.darkGray
        self.itemText = None

    # -------------------------------------------------------------------------
    def getObjs(self):
        data = [x[0] + x[1] for x in self.connectedObjects]
        return data

    # -------------------------------------------------------------------------
    def getRawObjs(self):
        return self.connectedObjects

    # -------------------------------------------------------------------------
    def setObjs(self, objs):
        self.connectedObjects = objs

    # -------------------------------------------------------------------------
    def setNamespace(self, nameSpace):
        self.connectedObjects = [[nameSpace, x[1]] for x in self.connectedObjects]

    # -------------------------------------------------------------------------
    def getNamespace(self):
        return list(set([x[0] for x in self.connectedObjects]))

    # -------------------------------------------------------------------------
    def setColor(self, newColor):
        self.currentColor = newColor
        self.setBrush(QBrush(self.currentColor))

    # -------------------------------------------------------------------------
    def getColor(self):
        return str(QColor(self.currentColor).name())

    # -------------------------------------------------------------------------
    def selectionColor(self):
        if self.isSelected():
            self.setBrush(QBrush(self.selectedColor))
        else:
            self.setBrush(QBrush(self.currentColor))

    # -------------------------------------------------------------------------
    def setText(self, itemText):
        if self.itemText is None:
            self.itemText = QGraphicsTextItem(itemText, self)
            self.itemText.setDefaultTextColor(QColor(Qt.black))
        else:
            self.itemText.setPlainText(itemText)
        tw = self.itemText.sceneBoundingRect()
        size = self.rect()
        self.itemText.setX(size.x() + (size.width() - tw.width()) / 2)
        self.itemText.setY(size.y() + (size.height() - tw.height()) / 2)

    # -------------------------------------------------------------------------
    def getText(self):
        if self.itemText is not None:
            return str(self.itemText.toPlainText())
        else:
            return ''


# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
class myEllipseItem(QGraphicsEllipseItem, BaseObjectClass):
    """Class based on QGraphicsEllipseItem to create my own Ellipse"""
    def __init__(self, x, y, w, objs):
        QGraphicsEllipseItem.__init__(self, x, y, w, w)
        BaseObjectClass.__init__(self, objs)
        self.setPen(QPen(Qt.NoPen))
        self.setColor(Qt.red)


# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
class myRectItem(QGraphicsRectItem, BaseObjectClass):
    """Class based on QGraphicsRectItem to create my own Rect"""
    def __init__(self, x, y, w, objs):
        QGraphicsRectItem.__init__(self, x, y, w, w)
        BaseObjectClass.__init__(self, objs)
        self.setPen(QPen(Qt.NoPen))
        self.setColor(Qt.red)


# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
class myFlagItem(QGraphicsPolygonItem, BaseObjectClass):
    """Class based on QGraphicsPolygonItem to create my own Flag Polygon"""
    def __init__(self, x, y, objs, siz=1):
        self.__polyCord = [[0, 30 * siz], [0, 0], [20 * siz, 10 * siz], [0, 20 * siz]]
        self.__direction = True

        self.__poly = QPolygonF()
        for pc in self.__polyCord:
            self.__poly.append(QPointF(x + pc[0], y + pc[1]))

        QGraphicsPolygonItem.__init__(self, self.__poly)
        BaseObjectClass.__init__(self, objs)

        self.setColor(Qt.red)

    # -------------------------------------------------------------------------
    def setColor(self, newColor):
        self.currentColor = newColor
        self.setPen(QPen(self.currentColor))

    # -------------------------------------------------------------------------
    def selectionColor(self):
        if self.isSelected():
            self.setPen(QPen(self.selectedColor))
        else:
            self.setPen(QPen(self.currentColor))

    # -------------------------------------------------------------------------
    def rect(self):
        return self.boundingRect()

    # -------------------------------------------------------------------------
    def setRect(self, adjust):
        dop = 1
        if all(adjust):
            dop = 1+adjust[2]/20.0

        poly = self.polygon()
        for num, pc in enumerate(self.__polyCord):
            self.__polyCord[num] = [poly[num].x(), poly[num].y()]

        base = self.__polyCord[1]
        self.__polyCord = [[(x[0] - base[0]) * dop, (x[1] - base[1]) * dop] for x in self.__polyCord]

        if adjust[0] == 2 and self.__direction and dop == 1:
            self.__polyCord[2][0] = -self.__polyCord[2][0]
            self.__direction = False
        elif adjust[0] == -2 and not self.__direction and dop == 1:
            self.__polyCord[2][0] = -self.__polyCord[2][0]
            self.__direction = True

        self.__poly = QPolygonF()
        for pc in self.__polyCord:
            self.__poly.append(QPointF(pc[0] + base[0], pc[1] + base[1]))
        self.setPolygon(self.__poly)

    # -------------------------------------------------------------------------
    def setDirection(self, dir):
        if self.__direction != dir:
            self.__direction = dir

            poly = self.polygon()
            for num, pc in enumerate(self.__polyCord):
                self.__polyCord[num] = [poly[num].x(), poly[num].y()]

            if self.__direction:
                self.__polyCord[2][0] += 40
            else:
                self.__polyCord[2][0] += -40

            self.__poly = QPolygonF()
            for pc in self.__polyCord:
                self.__poly.append(QPointF(pc[0], pc[1]))
            self.setPolygon(self.__poly)

    # -------------------------------------------------------------------------
    def getDirection(self):
        return self.__direction
