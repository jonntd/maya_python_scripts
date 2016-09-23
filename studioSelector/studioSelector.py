from PyQt4 import uic
import maya.cmds as cmds
import maya.mel as mel
from functools import partial

import re

from ikFkPashkanis import *
from functions import *
from flatWindowClass import *
from graphicsScene import *

storeNodeName = '_selectorAttrs'
curPath = dirname()

# -----------------------------------------------------------------------------
# Graphics View Class
# -----------------------------------------------------------------------------
class MyView(QGraphicsView):
    def __init__(self):
        QGraphicsView.__init__(self)

        self.setGeometry(QRect(0, 0, 100, 100))

        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setRubberBandSelectionMode(Qt.IntersectsItemShape)

        self.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        
        self.scene = GraphicsScene(self)
        self.scene.setSceneRect(QRectF())
        self.setScene(self.scene)
        self.setInteractive(True)

        self.backgroungImg = None
        self.backgroungImgFile = ''
        self.moveable = False
        
        self.nurbsSwitch = False
        self.isolateSwitch = 0

        self.popMenu = None

        self.__prevMousePos = None

        self.pxsize = None
        self.pxsizeX = None
        self.pxsizeY = None

    # -------------------------------------------------------------------------
    def addBackgroundImg(self, filename):
        self.backgroungImgFile = filename
        if self.backgroungImg is not None:
            self.scene.removeItem(self.backgroungImg)

        pixmap = QPixmap(filename)
        self.backgroungImg = self.scene.addPixmap(pixmap)
        self.backgroungImg.setZValue(-1)
        self.pxsize = pixmap.size()
        self.pxsizeX, self.pxsizeY = self.pxsize.width(), self.pxsize.height()
        self.scene.setSceneRect(QRectF(0, 0, float(self.pxsizeX), float(self.pxsizeY)))

    # -------------------------------------------------------------------------
    def wheelEvent(self, event):
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        scaleFactor = 1.15
        if event.delta() > 0:
            self.scale(scaleFactor, scaleFactor)
        else:
            self.scale(1.0 / scaleFactor, 1.0 / scaleFactor)

    # -------------------------------------------------------------------------
    def mousePressEvent(self, event):
        if event.button() == Qt.MidButton:
            self.__prevMousePos = event.pos()
        elif event.button() == Qt.RightButton:
            pass
        else:
            super(MyView, self).mousePressEvent(event)

    # -------------------------------------------------------------------------
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MidButton:
            offset = self.__prevMousePos - event.pos()
            self.__prevMousePos = event.pos()

            self.verticalScrollBar().setValue(self.verticalScrollBar().value() + offset.y())
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() + offset.x())
        else:
            super(MyView, self).mouseMoveEvent(event)

    # -------------------------------------------------------------------------
    def contextMenuEvent(self, event):
        self.popMenu = QMenu(None)
        self.popMenu.addAction(QIcon(curPath + '/ico/add_circle.png'),  'add circle',           lambda: self.on_action_add(event.pos(), 0))
        self.popMenu.addAction(QIcon(curPath + '/ico/add_rect.png'),    'add square',           lambda: self.on_action_add(event.pos(), 1))
        self.popMenu.addAction(QIcon(curPath + '/ico/add_flag.png'),    'add flag',             lambda: self.on_action_add(event.pos(), 2))
        self.popMenu.addAction(QIcon(curPath + '/ico/add_check.png'),   'add switch',           lambda: self.on_action_add_switch(event.pos(), event.globalPos()))
        self.popMenu.addAction(QIcon(curPath + '/ico/add_smooth.png'),  'add smooth button',    lambda: self.on_action_add(event.pos(), 4))
        self.popMenu.addAction(QIcon(curPath + '/ico/add_lkfk.png'),    'add Lk/Fk Bazhutkin',  lambda: self.on_action_add(event.pos(), 5))
        self.popMenu.addAction(QIcon(curPath + '/ico/add_lkfk.png'),    'add Lk/Fk Pashkanis',  lambda: self.on_action_add(event.pos(), 9))
        self.popMenu.addAction(QIcon(curPath + '/ico/select_all.png'),  'add "All" button',     lambda: self.on_action_add(event.pos(), 6))
        self.popMenu.addAction(QIcon(curPath + '/ico/add_nurbs.png'),   'add "Nurbs" button',   lambda: self.on_action_add(event.pos(), 7))
        self.popMenu.addAction(QIcon(curPath + '/ico/add_isolate.png'), 'add "Isolate" button', lambda: self.on_action_add(event.pos(), 8))
        self.popMenu.addAction(QIcon(curPath + '/ico/mirror.png'),      'add "Mirror" button',  lambda: self.on_action_add(event.pos(), 10))
        self.popMenu.addAction(QIcon(curPath + '/ico/mirror.png'),      'add "Mirror2" button', lambda: self.on_action_add(event.pos(), 11))
        self.popMenu.addAction(QIcon(curPath + '/ico/add_image.png'),   'set image',                    self.on_action_set_img)
        
        self.popMenu.exec_(event.globalPos())

    # -------------------------------------------------------------------------
    def on_action_set_img(self):
        fileName = QFileDialog.getOpenFileName(self, "Open Image", "", "Image Files (*.png *.jpg)")
        self.addBackgroundImg(fileName)

    # -------------------------------------------------------------------------
    def on_action_add_switch(self, pos, menuPos):
        objs = cmds.ls(selection=True)
        obj = objs[0]
        attrs = cmds.attributeInfo(obj, e=True)

        attrMenu = QMenu(None)
        for attr in attrs:
            attrMenu.addAction(attr, partial(self.on_action_add_checkbox, pos, obj, attr))
        attrMenu.exec_(menuPos)

    # -------------------------------------------------------------------------
    def on_action_add_checkbox(self, pos, obj, attr):
        try:
            nameSpace = cmds.referenceQuery(obj, ns=True)
            selData = [nameSpace[1:], obj.replace(nameSpace[1:], ''), attr]
        except:
            selData = ['', obj, attr]

        print(selData)

        scenePos = self.mapToScene(pos)

        check = DragCheckBox(attr)
        check.setType('check')
        check.setColor(Qt.darkGray)
        check.setMovable(self.moveable)
        check.setGeometry(scenePos.x(), scenePos.y(), 100, 18)
        check.setObjs(selData)

        item = self.scene.addWidget(check)
        item.setFlag(QGraphicsItem.ItemIsMovable, self.moveable)
        item.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.scene.addItem(item)

        self.connect(check, SIGNAL("toggled(bool)"), self.dragCheckBoxToggled)

    # -------------------------------------------------------------------------
    def dragCheckBoxToggled(self, data):
        chk = self.sender()
        attr = chk.getObjs()

        cmds.setAttr(attr, 1 if data else 0)

    # -------------------------------------------------------------------------
    def createBtn(self, btnName, btnType, btnColor, scenePos, fnc, btnPos=0, objs=[]):
        btnuser = DragButton(btnName)
        btnuser.setType(btnType)
        btnuser.setColor(btnColor)
        btnuser.setMovable(self.moveable)
        btnuser.setGeometry(scenePos.x()+btnPos, scenePos.y(), 55, 25)
        btnuser.setObjs(objs)
        item = self.scene.addWidget(btnuser)
        self.scene.addItem(item)

        self.connect(btnuser, SIGNAL("released()"), fnc)

        return item

    # -------------------------------------------------------------------------
    def on_action_add(self, pos, type):
        scenePos = self.mapToScene(pos)
        if scenePos.x() > 0 and scenePos.x() < self.pxsizeX and scenePos.y() > 0 and scenePos.y() < self.pxsizeY:
            item = None
            objs = cmds.ls(selection=True)
            selData = []
            for obj in objs:
                try:
                    nameSpace = cmds.referenceQuery(obj, ns=True)
                    selData.append([nameSpace[1:], obj.replace(nameSpace[1:], '')])
                except:
                    selData.append(['', obj])

            if type == 5:  # add Lk/Fk Bazhutkin
                self.createBtn('lk/fk keep', 'kinematik_keep', Qt.red,   scenePos, self.lkfkBtnClick)
                self.createBtn('lk/fk free', 'kinematik_free', Qt.green, scenePos, self.lkfkBtnClick, 60)
                return

            if type == 9:  # add Lk/Fk Pashkanis
                self.createBtn('lk/fk keep', 'p_kinematik_keep', Qt.red,   scenePos, self.lkfkPBtnClick)
                self.createBtn('lk/fk free', 'p_kinematik_free', Qt.green, scenePos, self.lkfkPBtnClick, 70)
                return

            if type == 6:  # add \"All\" button
                self.createBtn('all', 'all_controls', Qt.cyan, scenePos, self.allBtnClick)
                return

            if type == 7:  # add \"Nurbs\" button
                self.createBtn('nurbs', 'switch_nurbs', Qt.magenta, scenePos, self.nurbsBtnClick)
                return

            if type == 8:  # add \"Isolate\" button
                self.createBtn('isolate', 'switch_isolate', Qt.yellow, scenePos, self.isolateBtnClick)
                return

            if type == 10:  # add "Mirror" button
                self.createBtn('mirror', 'mirror_btn', Qt.blue, scenePos, self.mirrorBtnClick)
                return

            if type == 11:  # add "Mirror2" button
                self.createBtn('mirror2', 'mirror2_btn', Qt.blue, scenePos, self.mirrorBtn2Click)
                return

            if objs:
                if type == 0:  # add circle
                    item = myEllipseItem(scenePos.x(), scenePos.y(), 10, selData)
                elif type == 1:  # add square
                    item = myRectItem(scenePos.x(), scenePos.y(), 10, selData)
                elif type == 2:  # add flag
                    item = myFlagItem(scenePos.x(), scenePos.y(), selData)
                elif type == 4:  # add smooth button
                    item = self.createBtn('smooth', 'smooth', Qt.darkGray, scenePos, self.smoothBtnClick, objs=selData)

                item.setFlag(QGraphicsItem.ItemIsMovable, self.moveable)
                item.setFlag(QGraphicsItem.ItemIsSelectable, True)
                self.scene.addItem(item)

    # -------------------------------------------------------------------------
    def mirrorBtnClick(self):
        objs = cmds.ls(selection=True)
        print('-'*70)
        for obj in objs:
            data = obj.split(':')
            name = data[-1]
            prefix = ':'.join(data[:-1])
            if name.find('r_') == 0:
                mName = name.replace('r_', 'l_', 1)
            elif name.find('l_') == 0:
                mName = name.replace('l_', 'r_', 1)
            mObj = cmds.ls(prefix + ':' + mName)
            if mObj:
                cmds.setAttr(mObj[0] + '.rotateX', cmds.getAttr(obj + '.rotateX'))
                cmds.setAttr(mObj[0] + '.rotateY', cmds.getAttr(obj + '.rotateY'))
                cmds.setAttr(mObj[0] + '.rotateZ', cmds.getAttr(obj + '.rotateZ'))
                
                print('mirror: ' + obj + ' -> ' + mObj[0])

    # -------------------------------------------------------------------------
    # Mirror 2
    # -------------------------------------------------------------------------
    def findSide(self, ctrl):
        left_side = "l_"
        right_side = "r_"
        rez = re.findall(r""+left_side,ctrl)
        if len(rez)>0:
            return left_side, right_side
        rez = re.findall(r""+right_side,ctrl)
        if len(rez)>0:
            return right_side, left_side
        else:
            return None, None

    # -------------------------------------------------------------------------
    def findOppositeControl(self, selSide):
        allControls={}
        for ctrl in selSide:
            side, replace = self.findSide(ctrl)
            if side == None:
                continue
            spl = ctrl.rsplit(":",1)
            if len(spl) == 2:
                opp = spl[1].replace(side, replace ,1)
                opp = spl[0] + ":"+ opp
            else:
                opp = ctrl.replace(side, replace ,1)
            if cmds.objExists(ctrl):
                allControls[ctrl]=opp
        return allControls

    # -------------------------------------------------------------------------
    def setOppositeValue(self, allControls):
        for oneSide,otherSide in allControls.iteritems():
            negative = cmds.attributeQuery("negative", node=oneSide, exists=True)
            attrs = cmds.listAttr(oneSide, keyable=True, s=True)
            try:
                attrs.remove("visibility")
            except:
                pass
            for a in attrs:           
                value = cmds.getAttr(oneSide+"."+a)
       
                if (a[-1] != "X") and ("rotate" in a) and negative:  
                    value = value*-1
                if (a[-1] == "X") and ("translate" in a) and negative:  
                    value = value*-1
                try:
                    cmds.setAttr(otherSide+"."+a,value)
                except:
                    pass

    # -------------------------------------------------------------------------
    def mirrorBtn2Click(self):
        selSide = cmds.ls(sl=True, fl=True)
        allControls = self.findOppositeControl(selSide)
        self.setOppositeValue(allControls)

    # -------------------------------------------------------------------------
    # -------------------------------------------------------------------------
    def nurbsBtnClick(self):
        self.nurbsSwitch = False if self.nurbsSwitch else True

        panels = cmds.getPanel(type='modelPanel')
        for pan in panels:
            cmds.modelEditor(pan, e=True, nurbsCurves=self.nurbsSwitch)

    # -------------------------------------------------------------------------
    def getTopPos(self, objs):
        obj = objs[0]
        while True:
            curObj = cmds.pickWalk(obj, direction='up')
            if curObj[0] not in objs or obj == curObj[0]:
                break
            obj = curObj[0]
    
        return obj

    # -------------------------------------------------------------------------
    def isolateBtnClick(self):
        self.isolateSwitch = 0 if self.isolateSwitch else 1
        print('isolate')
        
        items = self.scene.items()
        outObjs = set()
        for item in items:
            itemType = type(item)
            if itemType == myEllipseItem or itemType == myRectItem:
                objs = item.getObjs()
                for obj in objs:
                    refObjs = cmds.referenceQuery(obj, n=True, dp=True)
                    outObjs = outObjs | set([self.getTopPos(refObjs)])

        print(list(outObjs))
        cmds.select(list(outObjs))
        panels = cmds.getPanel(type='modelPanel')
        for pan in panels:
            cmds.isolateSelect(pan, state=self.isolateSwitch)
        cmds.select(cl=True)

    # -------------------------------------------------------------------------
    def allBtnClick(self):
        allItems = self.scene.items()

        allObjs = []
        for item in allItems:
            itemType = type(item)
            if itemType == myEllipseItem or itemType == myRectItem or itemType == myFlagItem:
                objs = item.getObjs()
                if objs:
                    allObjs += objs

        cmds.select(allObjs)

    # -------------------------------------------------------------------------
    def lkfkBtnClick(self):
        btn = self.sender()
        kinType = btn.getType()
        if kinType == 'kinematik_free':
            mel.eval('human_switchFkIk "-sl"')
        else:
            mel.eval('human_changeFkIk "-sl"')
            
    # -------------------------------------------------------------------------
    def lkfkPBtnClick(self):
        btn = self.sender()
        kinType = btn.getType()

        obj = cmds.ls(selection=True, l=True)
        if obj:
            obj = obj[0]
            for x in fkIkData:
                if x in obj:
                    print('x', x)
                    selItems = self.scene.selectedItems()
                    if selItems:
                        item = selItems[0]
                        char = item.getNamespace()[0] + ':'
                        cmds.setAttr(char + fkIkData[x][0],fkIkData[x][1])
                        if kinType == 'p_kinematik_keep':
                            fkIkData[x][2](char)

        self.setItemsVisibility()

    # -------------------------------------------------------------------------
    def setItemsVisibility(self):
        allItems = self.scene.items()
        for item in allItems:
            itemType = type(item)
            if itemType == myEllipseItem or itemType == myRectItem:
                obj = item.getObjs()[0]
                vis = self.getObjVis(obj)
                item.setVisible(vis)

    # -------------------------------------------------------------------------
    def getObjVis(self, obj):
        path = cmds.ls(obj, l=True)
        if path:
            path = path[0]
        else:
            return False

        curVis = True
        for data in path.split('|'):
            if data:
                vis = cmds.getAttr(data + '.visibility')
                if type(vis) == type([]):
                    for x in vis:
                        if not x:
                            curVis = False
                            break
                else:
                    if not vis:
                        curVis = False
                        break
        return curVis

    # -------------------------------------------------------------------------
    def smoothBtnClick(self):
        btn = self.sender()
        objs = btn.getObjs()
        if btn.state:
            cmds.displaySmoothness(objs, divisionsU=3, divisionsV=3, pointsWire=16, pointsShaded=4, polygonObject=3)
            btn.state = False
        else:
            cmds.displaySmoothness(objs, divisionsU=0, divisionsV=0, pointsWire=4,  pointsShaded=1, polygonObject=1)
            btn.state = True

    # -------------------------------------------------------------------------
    def setItemSize(self, item, adjust):
        size = item.rect()
        size.adjust(adjust[0], adjust[1], adjust[2], adjust[3])

        itemType = type(item)
        if itemType == QGraphicsProxyWidget:
            item.widget().setRect(size, item.pos())
        elif itemType == myFlagItem:
            item.setRect(adjust)
        else:
            item.setRect(size)

    # -------------------------------------------------------------------------
    def keyPressEvent(self, e):
        key = e.key()
        selItems = self.scene.selectedItems()
        if key == Qt.Key_Minus:
            for item in selItems:
                self.setItemSize(item, [2, 2, -2, -2])

        elif key == Qt.Key_Plus:
            for item in selItems:
                self.setItemSize(item, [-2, -2, 2, 2])

        elif key == Qt.Key_Left:
            for item in selItems:
                self.setItemSize(item, [2, 0, -2, 0])

        elif key == Qt.Key_Right:
            for item in selItems:
                self.setItemSize(item, [-2, 0, 2, 0])

        elif key == Qt.Key_Up:
            for item in selItems:
                self.setItemSize(item, [0, -2, 0, 2])

        elif key == Qt.Key_Down:
            for item in selItems:
                self.setItemSize(item, [0, 2, 0, -2])

        elif key == Qt.Key_Delete:
            for item in selItems:
                self.scene.removeItem(item)

        else:
            super(MyView, self).keyPressEvent(e)
                

# -----------------------------------------------------------------------------
# MDI SubWindow Class
# -----------------------------------------------------------------------------
class subWindow(QMdiSubWindow):
    def __init__(self, parent, name):
        self.windowName = str(name)
        self.windowFile = ''
        super(subWindow, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowTitle(name)
        self.setWindowIcon(QIcon(curPath + '/ico/3d65.png'))
        
        self.popMenu = self.systemMenu()
        self.popMenu.addSeparator()
        self.popMenu.addAction(QIcon(curPath + '/ico/ic_create_black600_48dp.png'), 'rename', self.renamePage)

        self.view = MyView()
        self.setWidget(self.view)
        self.showMaximized()

    # -------------------------------------------------------------------------
    def __del__(self):
        attrs = takeAllData(storeNodeName)
        for attr in attrs:
            param = takeData(storeNodeName, attr)
            if param == self.windowFile:
                deleteData(storeNodeName, attr)

    # -------------------------------------------------------------------------
    def renamePage(self):
        name, ok = QInputDialog.getText(self, 'Set page name', 'Name:')
        if ok:
            self.windowName = str(name)
            self.setWindowTitle(self.windowName)


# -----------------------------------------------------------------------------
# Main Dialog class
# -----------------------------------------------------------------------------
class MainForm(QDialog, FlatWindow):
    def __init__(self, parent=getMayaWindow()):
        super(MainForm, self).__init__(parent)
        FlatWindow.__init__(self, MainForm)
        uic.loadUi(curPath + '/main_left.ui', self)
        self.loadWnd()

        refs = cmds.ls(rf=True)
        for ref in refs:
            try:
                nameSpace = cmds.referenceQuery(ref, ns=True)
                self.namespaceComboBox.addItem(nameSpace[1:])
            except:
                pass

        attrs = takeAllData(storeNodeName)
        for attr in attrs:
            fileName = takeData(storeNodeName, attr)
            self.openFileName(fileName)

        self.addScriptJob()

        self.connect(self.changeColorBtn, SIGNAL("released()"), self.changeColorBtnClick)
        self.connect(self.changeNameEdit, SIGNAL("editingFinished()"), self.changeNameEditChanged)
        self.connect(self.setEditCheckBox, SIGNAL("toggled(bool)"), self.setEditCheckBoxToggled)
        self.connect(self.namespaceComboBox, SIGNAL("currentIndexChanged(const QString &)"), self.namespaceComboBoxCnanged)
        self.connect(self.newBtn,  SIGNAL("released()"), self.newBtnClick)
        self.connect(self.openBtn, SIGNAL("released()"), self.openBtnClick)
        self.connect(self.saveBtn, SIGNAL("released()"), self.saveBtnClick)
        self.connect(self.closeBtn, SIGNAL("released()"), self.closeWnd)
        self.connect(self, SIGNAL("finished(int)"), lambda x: self.delScriptJob())

        self.connect(self.singleCheckBox, SIGNAL("toggled(bool)"), self.singleCheckBoxToggled)

    # -------------------------------------------------------------------------
    def singleCheckBoxToggled(self, state):
        print('state', state)
        curWnd = self.getCurWnd()
        if curWnd is not None:
            curWnd.view.scene.singleFlag = state

    # -------------------------------------------------------------------------
    def closeWnd(self):
        self.saveWnd()
        self.accept()

    # -------------------------------------------------------------------------
    def saveWnd(self):
        geo = self.geometry()
        cmds.optionVar(iv=('selector_geo_x',geo.x()))
        cmds.optionVar(iv=('selector_geo_y',geo.y()))
        cmds.optionVar(iv=('selector_geo_w',geo.width()))
        cmds.optionVar(iv=('selector_geo_h',geo.height()))

    # -------------------------------------------------------------------------
    def loadWnd(self):
        x = cmds.optionVar(q='selector_geo_x')
        y = cmds.optionVar(q='selector_geo_y')
        w = cmds.optionVar(q='selector_geo_w')
        h = cmds.optionVar(q='selector_geo_h')

        if all([(q != 0) for q in [x,y,w,h]]):
            geo = QRect(x,y,w,h)
            self.setGeometry(geo)

    # -------------------------------------------------------------------------
    def addScriptJob(self):
        self.sJob = cmds.scriptJob(event=['SelectionChanged', self.selectionChangedScript])

    # -------------------------------------------------------------------------
    def delScriptJob(self):
        cmds.scriptJob(kill=self.sJob, force=True)

    # -------------------------------------------------------------------------
    def selectionChangedScript(self):
        objs = cmds.ls(selection=True)
        curWnd = self.getCurWnd()
        items = curWnd.view.scene.items()

        curWnd.view.scene.setSelectionSignal(False)
        if objs:
            for item in items:
                itemType = type(item)
                if itemType == myEllipseItem or itemType == myRectItem or itemType == myFlagItem:
                    itemData = item.getObjs()
                    if len(itemData) == len(set(itemData) & set(objs)):
                        item.setSelected(True)
                    else:
                        item.setSelected(False)
                    curWnd.view.scene.setSelectionColor(item)
        else:
            for item in items:
                itemType = type(item)
                if itemType == myEllipseItem or itemType == myRectItem or itemType == myFlagItem:
                    item.setSelected(False)
                    curWnd.view.scene.setSelectionColor(item)
        curWnd.view.scene.setSelectionSignal(True)

    # -------------------------------------------------------------------------
    def namespaceComboBoxCnanged(self, data):
        #print('data', data)
        curWnd = self.getCurWnd()
        items = curWnd.view.scene.items()
        #print('items', len(items))
        for item in items:
            itemType = type(item)
            #print('item', itemType, item)
            if itemType == myEllipseItem or itemType == myRectItem or itemType == myFlagItem:
                item.setNamespace(str(data))
                curWnd.view.setItemsVisibility()

    # -------------------------------------------------------------------------
    def setEditCheckBoxToggled(self, flag):
        curWnd = self.getCurWnd()
        if curWnd is not None:
            items = curWnd.view.scene.items()
            curWnd.view.moveable = flag
    
            for item in items:
                itemType = type(item)
    
                if itemType == myEllipseItem or itemType == myRectItem or itemType == myFlagItem:
                    item.setFlag(QGraphicsItem.ItemIsMovable, flag)
    
                elif itemType == QGraphicsProxyWidget:
                    item.widget().setMovable(flag)

    # -------------------------------------------------------------------------
    def getRealItemPos(self, item):
        pos = item.pos()
        rect = item.rect()
        itemPos = [rect.x()+pos.x(), rect.y()+pos.y(), rect.width(), rect.height()]
        return itemPos

    # -------------------------------------------------------------------------
    def newBtnClick(self):
        newItem = subWindow(self.mdiArea, 'untitled')
        state = self.setEditCheckBox.checkState()
        newItem.view.moveable = True if state > 0 else False
        newItem.view.scene.mainWnd = self

    # -------------------------------------------------------------------------
    def createGeometryItem(self, wnd, geometry, item):
        obj = geometry(0, 0, 30, item['objs'])
        obj.setRect(item['pos'][0], item['pos'][1], item['pos'][2], item['pos'][3])
        obj.setFlag(QGraphicsItem.ItemIsMovable, wnd.view.moveable)
        obj.setFlag(QGraphicsItem.ItemIsSelectable, True)
        obj.setColor(QColor(item['color']))
        obj.setText(item['name'])
        wnd.view.scene.addItem(obj)

    # -------------------------------------------------------------------------
    def createFlagItem(self, wnd, item):
        obj = myFlagItem(item['pos'][0], item['pos'][1], item['objs'], item['pos'][2]/20.0)
        obj.setDirection(item['dir'])
        obj.setFlag(QGraphicsItem.ItemIsMovable, wnd.view.moveable)
        obj.setFlag(QGraphicsItem.ItemIsSelectable, True)
        obj.setColor(QColor(item['color']))
        wnd.view.scene.addItem(obj)

    # -------------------------------------------------------------------------
    def createWidgetItem(self, wnd, widget, item, wtype):
        wdt = widget(item['name'])
        wdt.setType(wtype)
        wdt.setColor(QColor(item['color']))
        wdt.setMovable(wnd.view.moveable)
        wdt.setGeometry(item['pos'][0], item['pos'][1], item['pos'][2], item['pos'][3])
        wdt.setObjs(item['objs'])
        wdtItem = wnd.view.scene.addWidget(wdt)
        wdtItem.setFlag(QGraphicsItem.ItemIsSelectable, True)
        wnd.view.scene.addItem(wdtItem)
        return wdt

    # -------------------------------------------------------------------------
    def openBtnClick(self):
        importFileName = QFileDialog.getOpenFileName(self, "Open Selector", "", "Selector Files (*.selector)")
        if not importFileName:
            return
        self.openFileName(importFileName)

    # -------------------------------------------------------------------------
    def openFileName(self, importFileName):
        loadItems = loadSettings(importFileName)
        newItem = subWindow(self.mdiArea, 'test')
        newItem.view.scene.mainWnd = self
        newItem.windowFile = str(importFileName)
        state = self.setEditCheckBox.checkState()
        newItem.view.moveable = True if state > 0 else False

        for item in loadItems:
            if item['type'] == 'winName':
                newItem.setWindowTitle(item['name'])
                newItem.windowName = item['name']

            elif item['type'] == 'pixmap':
                newItem.view.addBackgroundImg(item['fileName'])

            elif item['type'] == 'rect':
                self.createGeometryItem(newItem, myRectItem, item)

            elif item['type'] == 'ellipse':
                self.createGeometryItem(newItem, myEllipseItem, item)

            elif item['type'] == 'flag':
                self.createFlagItem(newItem, item)

            elif item['type'] == 'smooth':
                btnuser = self.createWidgetItem(newItem, DragButton, item, 'smooth')
                self.connect(btnuser, SIGNAL("released()"), newItem.view.smoothBtnClick)

            elif item['type'] == 'kinematik_keep':
                btnuser = self.createWidgetItem(newItem, DragButton, item, 'kinematik_keep')
                self.connect(btnuser, SIGNAL("released()"), newItem.view.lkfkBtnClick)

            elif item['type'] == 'kinematik_free':
                btnuser = self.createWidgetItem(newItem, DragButton, item, 'kinematik_free')
                self.connect(btnuser, SIGNAL("released()"), newItem.view.lkfkBtnClick)

            elif item['type'] == 'p_kinematik_keep':
                btnuser = self.createWidgetItem(newItem, DragButton, item, 'p_kinematik_keep')
                self.connect(btnuser, SIGNAL("released()"), newItem.view.lkfkPBtnClick)

            elif item['type'] == 'p_kinematik_free':
                btnuser = self.createWidgetItem(newItem, DragButton, item, 'p_kinematik_free')
                self.connect(btnuser, SIGNAL("released()"), newItem.view.lkfkPBtnClick)

            elif item['type'] == 'all_controls':
                btnuser = self.createWidgetItem(newItem, DragButton, item, 'all_controls')
                self.connect(btnuser, SIGNAL("released()"), newItem.view.allBtnClick)

            elif item['type'] == 'check':
                check = self.createWidgetItem(newItem, DragCheckBox, item, 'check')
                self.connect(check, SIGNAL("toggled(bool)"), newItem.view.dragCheckBoxToggled)

            elif item['type'] == 'switch_nurbs':
                btnuser = self.createWidgetItem(newItem, DragButton, item, 'nurbs')
                self.connect(btnuser, SIGNAL("released()"), newItem.view.nurbsBtnClick)

            elif item['type'] == 'switch_isolate':
                btnuser = self.createWidgetItem(newItem, DragButton, item, 'isolate')
                self.connect(btnuser, SIGNAL("released()"), newItem.view.isolateBtnClick)

            elif item['type'] == 'mirror_btn':
                btnuser = self.createWidgetItem(newItem, DragButton, item, 'mirror')
                self.connect(btnuser, SIGNAL("released()"), newItem.view.mirrorBtnClick)

            elif item['type'] == 'mirror2_btn':
                btnuser = self.createWidgetItem(newItem, DragButton, item, 'mirror2')
                self.connect(btnuser, SIGNAL("released()"), newItem.view.mirrorBtn2Click)

        attrs = takeAllData(storeNodeName)
        flag = True
        for attr in attrs:
            if takeData(storeNodeName, attr) == importFileName:
                flag = False
        if flag:
            storeData(storeNodeName, 'File' + str(len(attrs)+1), importFileName, 'string')

        newItem.view.setItemsVisibility()


    # -------------------------------------------------------------------------
    def saveBtnClick(self):
        exportFileName = QFileDialog.getSaveFileName(self, "Save Selector", "", "Selector Files (*.selector)")
        if not exportFileName:
            return

        curWnd = self.getCurWnd()
        items = curWnd.view.scene.items()

        exportItems = []

        for item in items:
            itemType = type(item)
            if itemType == myEllipseItem:
                exportItems.append({'type': 'ellipse', 'pos': self.getRealItemPos(item),
                                    'color': item.getColor(), 'objs': item.getRawObjs(), 'name': item.getText()})

            elif itemType == myRectItem:
                exportItems.append({'type': 'rect', 'pos': self.getRealItemPos(item),
                                    'color': item.getColor(), 'objs': item.getRawObjs(), 'name': item.getText()})
                
            elif itemType == myFlagItem:
                exportItems.append({'type': 'flag', 'pos': self.getRealItemPos(item),
                                    'color': item.getColor(), 'objs': item.getRawObjs(), 'name': item.getText(),
                                    'dir': item.getDirection()})

            elif itemType == QGraphicsProxyWidget:
                exportItems.append({'type': item.widget().getType(), 'pos': self.getRealItemPos(item),
                                    'color': item.widget().getColor(), 'objs': item.widget().getRawObjs(),
                                    'name': str(item.widget().text())})

            elif itemType == QGraphicsPixmapItem:
                fileName = curWnd.view.backgroungImgFile
                exportItems.append({'type': 'pixmap', 'fileName': str(fileName)})

        exportItems.append({'type': 'winName', 'name': curWnd.windowName})
        saveSettings(exportItems, exportFileName)

    # -------------------------------------------------------------------------
    def getCurWnd(self):
        curWnd = self.mdiArea.activeSubWindow()
        if curWnd is None:
            wndList = self.mdiArea.subWindowList()
            if len(wndList) == 1:
                curWnd = wndList[0]

        return curWnd

    # -------------------------------------------------------------------------
    def changeColorBtnClick(self):
        curWnd = self.getCurWnd()
        items = curWnd.view.scene.selectedItems()
        curColor = QColorDialog.getColor()

        for item in items:
            itemType = type(item)
            if itemType == myEllipseItem or itemType == myRectItem or itemType == myFlagItem:
                item.setColor(curColor)
            elif itemType == QGraphicsProxyWidget:
                item.widget().setColor(curColor)

    # -------------------------------------------------------------------------
    def changeNameEditChanged(self):
        data = self.changeNameEdit.text()
        curWnd = self.getCurWnd()
        items = curWnd.view.scene.selectedItems()

        for item in items:
            itemType = type(item)
            if itemType == myEllipseItem or itemType == myRectItem or itemType == myFlagItem:
                item.setText(data)
            elif itemType == QGraphicsProxyWidget:
                item.widget().setText(data)


# -----------------------------------------------------------------------------
# window
# -----------------------------------------------------------------------------
def studioSelector():
    wnd = MainForm()
    wnd.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
    wnd.show()

#studioSelector()
