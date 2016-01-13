#############################################################################
# Texture Spreadsheet Window
# nikopol.vfx 2015/09/14
#############################################################################

import os
import sys
import sip
import maya.OpenMayaUI as mui
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import uic
import maya.cmds as cmds
import pymel.core as pc
import maya.mel as mel

from functools import partial
from studioLibs import FlatWindowClass as flat

#----------------------------------------------------------------------
def getMayaWindow():
    ptr = mui.MQtUtil.mainWindow()
    return sip.wrapinstance(long(ptr), QObject)

#----------------------------------------------------------------------
def dirname():
    encoding = sys.getfilesystemencoding()
    path = os.path.dirname(unicode(os.path.abspath(__file__), encoding)).replace('\\', '/')
    os.chdir(path)
    return path
    
#----------------------------------------------------------------------
curPath = dirname()
os.chdir(curPath)

#----------------------------------------------------------------------
# main window class
#----------------------------------------------------------------------
class TextureSpreadsheetWnd(QDialog, flat.FlatWindow):
    def __init__(self, parent=getMayaWindow()):
        super(TextureSpreadsheetWnd, self).__init__(parent)
        flat.FlatWindow.__init__(self, TextureSpreadsheetWnd)
        uic.loadUi('textureSpreadsheet.ui', self)
        
        self.filterTypes = ['Off', 'Mipmap', 'Box', 'Quadratic', 'Quartic', 'Gaussian']
        self.gammaTypes = ['Linear', 'Gamma', 'sRGB', '']
        self.extentions = ['exr', 'tif', 'tex', 'tx']

        self.grayColorSpin = 'QCheckBox { background: #f0f0f0; }'
        self.redColorSpin  = 'QCheckBox { background: #ffa0a0; }'

        self.textureTable.horizontalHeader().setStretchLastSection(True)
        self.setupNodeTable()

        self.connect(self.reloadBtn,         SIGNAL("released()"),                      self.setupNodeTable)
        self.connect(self.filterSpinBox,     SIGNAL("valueChanged(double)"),            self.filterSpinChanged)
        self.connect(self.gammaCombo,        SIGNAL("currentIndexChanged(int)"),        self.allGammaCombo)
        self.connect(self.filterCombo,       SIGNAL("currentIndexChanged(int)"),        self.allFilterCombo)
        self.connect(self.textureTable,      SIGNAL("cellDoubleClicked (int, int)"),    self.textureTableClicked)
        self.connect(self.textureTable,      SIGNAL("itemChanged(QTableWidgetItem *)"), self.textureNameChanged)
        self.connect(self.extensionCombo,    SIGNAL("currentIndexChanged(int)"),        self.allExtensionCombo)
        self.connect(self.enableGamma1Btn,   SIGNAL("released()"), lambda: self.allCheckBox('vrayFileGammaEnable', 0, 3))
        self.connect(self.enableGamma2Btn,   SIGNAL("released()"), lambda: self.allCheckBox('vrayFileGammaEnable', 1, 3))
        self.connect(self.allowNegative1Btn, SIGNAL("released()"), lambda: self.allCheckBox('vrayFileAllowNegColors', 0, 4))
        self.connect(self.allowNegative2Btn, SIGNAL("released()"), lambda: self.allCheckBox('vrayFileAllowNegColors', 1, 4))
        self.connect(self.prefixEdit,        SIGNAL("editingFinished()"),               self.prefixEditEdit)
        self.connect(self.slashButton,       SIGNAL("released()"),                      self.slashButtonClick)
        self.connect(self.changeFolderBtn,   SIGNAL("released()"),                      self.changeFolderBtnClick)


    #------------------------------------------------------------------
    def textureTableClicked(self, row, col):
        if col == 0:
            node = str(self.textureTable.item(row, 0).text())
            cmds.select(node)


    #------------------------------------------------------------------
    def setupNodeTable(self):
        # clear table
        row = self.textureTable.rowCount()
        for x in range(row):
            self.textureTable.removeRow(0)

        # fill again
        nodes = cmds.ls(type='file')
        for node in nodes:
            row = self.textureTable.rowCount()
            self.textureTable.insertRow(row)

            #----------------------------------------------------------
            # row 0: add node name
            newItem = QTableWidgetItem(node)
            newItem.setFlags(newItem.flags() ^ Qt.ItemIsEditable)
            self.textureTable.setItem(row, 0, newItem)

            #----------------------------------------------------------
            # row 1: add comboBox 'Filter Type'
            newCombo = QComboBox()
            newCombo.addItems(self.filterTypes)

            curAttr = 'filterType'
            curID = myGetAttr(node, curAttr)
            newCombo.setCurrentIndex(curID)

            self.textureTable.setCellWidget(row, 1, newCombo)
            self.connect(newCombo, SIGNAL("currentIndexChanged(int)"), partial(self.attrChanged, node=str(node), attr=curAttr, type=0))

            #----------------------------------------------------------
            # row 2: add spinbox 'Filter'
            newSpin = QDoubleSpinBox()

            curAttr = 'filter'
            curValue = myGetAttr(node, curAttr)
            newSpin.setValue(curValue)
            newSpin.setSingleStep(0.1)

            self.textureTable.setCellWidget(row, 2, newSpin)
            self.connect(newSpin, SIGNAL("valueChanged(double)"), partial(self.attrChanged, node=str(node), attr=curAttr, type=0))

            #----------------------------------------------------------
            # row 3: add checkBox 'Enable Gamma'
            newCheck = QCheckBox('Enable')

            curAttr = 'vrayFileGammaEnable'
            curValue = myGetAttr(node, curAttr, -1)
            if curValue != -1:
                newCheck.setCheckState(curValue*2)
                newCheck.setStyleSheet(self.grayColorSpin)
            else:
                newCheck.setCheckState(0)
                newCheck.setStyleSheet(self.redColorSpin)

            self.textureTable.setCellWidget(row, 3, newCheck)
            self.connect(newCheck, SIGNAL("stateChanged(int)"), partial(self.attrChanged, node=str(node), attr=curAttr, type=0))

            #----------------------------------------------------------
            # row 4: add checkBox 'Allow Negative'
            newCheck = QCheckBox('Allow')

            curAttr = 'vrayFileAllowNegColors'
            curValue = myGetAttr(node, curAttr, -1)
            if curValue != -1:
                newCheck.setCheckState(curValue*2)
                newCheck.setStyleSheet(self.grayColorSpin)
            else:
                newCheck.setCheckState(0)
                newCheck.setStyleSheet(self.redColorSpin)

            self.textureTable.setCellWidget(row, 4, newCheck)
            self.connect(newCheck, SIGNAL("stateChanged(int)"), partial(self.attrChanged, node=str(node), attr=curAttr, type=1))

            #----------------------------------------------------------
            # row 5: add comboBox 'Gamma'
            newCombo = QComboBox()
            newCombo.addItems(self.gammaTypes)

            curAttr = 'vrayFileColorSpace'
            curID = myGetAttr(node, curAttr, len(self.gammaTypes)+1)
            newCombo.setCurrentIndex(curID)

            self.textureTable.setCellWidget(row, 5, newCombo)
            self.connect(newCombo, SIGNAL("currentIndexChanged(int)"), partial(self.attrChanged, node=str(node), attr=curAttr, type=0))


            #----------------------------------------------------------
            # row 6: add file name
            fileName = cmds.getAttr(node + '.fileTextureName')
            newItem = QTableWidgetItem(fileName)
            self.textureTable.setItem(row, 6, newItem)


    #------------------------------------------------------------------
    def attrChanged(self, data, node, attr, type):
        isAttr = pc.listAttr(node, st=attr)
        if not isAttr:
            addvRayAttrs(node, type)
        cmds.setAttr(node + '.' + attr, data)

        obj = self.sender()
        obj.setStyleSheet(self.grayColorSpin)


    #------------------------------------------------------------------
    def textureNameChanged(self, data):
        col = self.textureTable.column(data)
        if col == 6:
            row = self.textureTable.row(data)
            node = str(self.textureTable.item(row, 0).text())
            newText = str(data.text())
            cmds.setAttr(node + '.fileTextureName', newText, type='string')


    #------------------------------------------------------------------
    def allFilterCombo(self, data):
        if data != 6:
            items = self.textureTable.selectedItems()
            for item in items:
                col = self.textureTable.column(item)
                if col == 0:
                    row = self.textureTable.row(item)
                    node = str(self.textureTable.item(row, 0).text())
                    self.attrChanged(data, node, 'filterType', 0)
                    
                    combo = self.textureTable.cellWidget(row, 1)
                    combo.setCurrentIndex(data)

        self.filterCombo.setCurrentIndex(6)


    #------------------------------------------------------------------
    def allGammaCombo(self, data):
        if data != 3:
            items = self.textureTable.selectedItems()
            for item in items:
                col = self.textureTable.column(item)
                if col == 0:
                    row = self.textureTable.row(item)
                    node = str(self.textureTable.item(row, 0).text())
                    self.attrChanged(data, node, 'vrayFileColorSpace', 0)
                    
                    combo = self.textureTable.cellWidget(row, 5)
                    combo.setCurrentIndex(data)

        self.gammaCombo.setCurrentIndex(3)


    #------------------------------------------------------------------
    def filterSpinChanged(self, data):
        items = self.textureTable.selectedItems()
        for item in items:
            col = self.textureTable.column(item)
            if col == 0:
                row = self.textureTable.row(item)
                node = str(self.textureTable.item(row, 0).text())
                self.attrChanged(data, node, 'filter', 0)

                spin = self.textureTable.cellWidget(row, 2)
                spin.setValue(data)


    #------------------------------------------------------------------
    def allCheckBox(self, attr, data, pos):
        type = 1 if attr == 'vrayFileAllowNegColors' else 0        
        items = self.textureTable.selectedItems()
        for item in items:
            col = self.textureTable.column(item)
            if col == 0:
                row = self.textureTable.row(item)
                node = str(self.textureTable.item(row, 0).text())
                self.attrChanged(data, node, attr, type)
                
                check = self.textureTable.cellWidget(row, pos)
                check.setCheckState(data*2)


    #------------------------------------------------------------------
    def allExtensionCombo(self, data):
        if data != 4:
            items = self.textureTable.selectedItems()
            for item in items:
                col = self.textureTable.column(item)
                if col == 0:
                    row = self.textureTable.row(item)
                    node = str(self.textureTable.item(row, 0).text())
                    texture = str(self.textureTable.item(row, 6).text())
                    temp = '.'.join(texture.split('.')[:-1]) + '.' + self.extentions[data]
                    cmds.setAttr(node + '.fileTextureName', temp, type='string')
                    self.textureTable.item(row, 6).setText(temp)

        self.extensionCombo.setCurrentIndex(4)


    #------------------------------------------------------------------
    def prefixEditEdit(self):
        data = self.prefixEdit.text()
        
        items = self.textureTable.selectedItems()
        for item in items:
            col = self.textureTable.column(item)
            if col == 0:
                row = self.textureTable.row(item)
                node = str(self.textureTable.item(row, 0).text())
                texture = str(self.textureTable.item(row, 6).text())
                temp = data + '/' + '/'.join(texture.split('/')[1:])
                self.textureTable.item(row, 6).setText(temp)


    #------------------------------------------------------------------
    def slashButtonClick(self):
        items = self.textureTable.selectedItems()
        for item in items:
            col = self.textureTable.column(item)
            if col == 0:
                row = self.textureTable.row(item)
                node = str(self.textureTable.item(row, 0).text())
                texture = str(self.textureTable.item(row, 6).text())
                temp = texture.replace('\\', '/')
                self.textureTable.item(row, 6).setText(temp)


    #------------------------------------------------------------------
    def changeFolderBtnClick(self):
        folder = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        if not folder:
            return
        folder = folder.replace('\\', '/') + '/'
        #print('folder', folder)
        items = self.textureTable.selectedItems()
        for item in items:
            col = self.textureTable.column(item)
            if col == 0:
                row = self.textureTable.row(item)
                node = str(self.textureTable.item(row, 0).text())
                texture = str(self.textureTable.item(row, 6).text())
                fileName = texture.split('/')[-1]
                newName = folder + fileName
                #print(row, node, texture, folder + fileName)
                self.textureTable.item(row, 6).setText(newName)


#----------------------------------------------------------------------
def addvRayAttrs(node, type):
    if type == 1:
        attrs = ['vrayFileAllowNegColors']
    else:
        attrs = ['vrayFileGammaEnable', 'vrayFileColorSpace', 'vrayFileGammaValue']

    for attr in attrs:
        mel.eval('vrayAddAttr ' + str(node) + ' ' + attr + ';')


#----------------------------------------------------------------------
def myGetAttr(node, attr, default=False):
    data = default
    isAttrName = pc.listAttr(str(node), st=attr)
    if isAttrName:
        data = cmds.getAttr(str(node) + '.' + attr)

    return data


#----------------------------------------------------------------------
# window
def textureSpreadsheet():
    formCollect = TextureSpreadsheetWnd()
    formCollect.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
    formCollect.show()


#----------------------------------------------------------------------
# MAIN
#textureSpreadsheet()






