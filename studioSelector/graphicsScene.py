import maya.cmds as cmds

from graphicsItems import *
from widgetItems import *


# -----------------------------------------------------------------------------
# Graphics Scene Class
# -----------------------------------------------------------------------------
class GraphicsScene(QGraphicsScene):
    def __init__(self, parent=None):
        super(GraphicsScene, self).__init__(parent)
        self.parent = parent
        self.selItems = []
        self.mainWnd = None
        self.singleFlag = False

        self.setSelectionSignal(True)

    # -------------------------------------------------------------------------
    def setSelectionSignal(self, flag):
        if flag:
            self.connect(self, SIGNAL("selectionChanged()"), self.sceneSelectionChanged)
        else:
            self.disconnect(self, SIGNAL("selectionChanged()"), self.sceneSelectionChanged)

    # -------------------------------------------------------------------------
    def mouseReleaseEvent(self, event):
        if QApplication.keyboardModifiers() == Qt.ShiftModifier:
            for item in self.selItems:
                item.setSelected(True)
            self.selItems = self.selectedItems()
        else:
            self.selItems = self.selectedItems()
            return QGraphicsScene.mouseReleaseEvent(self, event)

    # -------------------------------------------------------------------------
    def sceneSelectionChanged(self):
        items = self.selectedItems()
        cmds.select(cl=True)

        for item in items:
            itemType = type(item)
            if itemType == myEllipseItem or itemType == myRectItem or itemType == myFlagItem:
                objs = item.getObjs()
                #print('flag', self.singleFlag)
                if objs and not self.singleFlag:
                    cmds.select(objs, add=True)

        items = self.items()
        for item in items:
            self.setSelectionColor(item)

    # -------------------------------------------------------------------------
    def setSelectionColor(self, item):
        itemType = type(item)
        if itemType == myEllipseItem or itemType == myRectItem or itemType == myFlagItem:
            item.selectionColor()
        elif itemType == QGraphicsProxyWidget:
            item.widget().selectionColor(item.isSelected())
