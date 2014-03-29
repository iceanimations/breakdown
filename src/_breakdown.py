from uiContainer import uic
from PyQt4.QtGui import *
from PyQt4.QtCore import Qt
import qtify_maya_window as qtfy
import os.path as osp
import backend
reload(backend)
be = backend.be
import util
reload(util)
from customui import ui as cui
reload(cui)
import pymel.core as pc

rootPath = osp.dirname(osp.dirname(__file__))
uiPath = osp.join(rootPath, 'ui')
iconPath = osp.join(rootPath, 'icons')

Form, Base = uic.loadUiType(osp.join(uiPath, 'breakdown.ui'))
class Breakdown(Form, Base):
    def __init__(self, parent=qtfy.getMayaWindow()):
        super(Breakdown, self).__init__(parent)
        self.setupUi(self)
        
        self.redItems = []
        self.redIcon = QIcon(osp.join(iconPath, 'red.png'))
        self.greenIcon = QIcon(osp.join(iconPath, 'green.png'))
        self.itemsBox = self.addScroller('All References')
        self.projects = {}
        
        self.projectsBox.activated.connect(self.addItems)
        self.refreshButton.clicked.connect(self.refresh)
        self.updateButton.clicked.connect(self.update)
        self.selectAllButton.clicked.connect(self.selectAll)
        self.filterButton.clicked.connect(self.filterRed)
        
        self.setProjectBox()
        
    def setProjectBox(self):
        projs = util.get_all_projects()
        for project in projs:
            self.projects[project['title']] = project['code']
            self.projectsBox.addItem(project['title'])
        
    def addItems(self):
        project = str(self.projectsBox.currentText())
        if project == '--Select Project--':
            return
        refs = be.check_scene(self.projects[project])
        for ref in refs:
            refNode = str(ref.refNode)
            if refs[ref]:
                item = self.createItem(osp.basename(ref.path),
                                       self.button(self.redIcon),
                                       subTitle=refNode,
                                       detail='Loaded' if ref.isLoaded() else 'Unloaded')
                self.redItems.append(item)
            else:
                item = self.createItem(osp.basename(ref.path),
                                       self.button(self.greenIcon),
                                       subTitle=refNode,
                                       detail='Loaded' if ref.isLoaded() else 'Not Loaded')
            self.itemsBox.addItem(item)
            item.setObjectName(str(ref.path) +'>'+ refNode + str('>'+ refs[ref]) if refs[ref] else '')
        map(lambda widget: self.bindClickEvent(widget), self.itemsBox.items())
        
    def bindClickEvent(self, widget):
        widget.mouseReleaseEvent = lambda event: self.handleItemClick(event, widget)
        
    def handleItemClick(self, event, widget):
        if event.button() == Qt.LeftButton:
            widget.setChecked(not widget.isChecked())
            self.handleSelectAllButton()
            
    def referenceNodeAndPath(self, widget):
        data = str(widget.objectName())
        path, refNode, newPath = data.split('>')
        return pc.system.FileReference(pathOrRefNode=path, refnode=refNode), newPath 
    
    def createItem(self, title, btn, subTitle='', thirdTitle='', detail=''):
        item = cui.Item(self)
        item.setTitle(title)
        item.setSubTitle(subTitle)
        item.setThirdTitle(thirdTitle)
        item.setDetail(detail)
        item.addWidget(btn)
        return item
    
    def clearItems(self):
        self.itemsBox.clearItems()
        del self.redItems[:]
    
    def selectAll(self):
        if not self.redItems:
            pc.warning('No Red Items found...')
        for item in self.redItems:
            item.setChecked(self.selectAllButton.isChecked())
        
    def handleSelectAllButton(self):
        flag = True
        for item in self.redItems:
            if not item.isChecked():
                flag = False
                break
        if self.redItems:
            self.selectAllButton.setChecked(flag)
    
    def filterRed(self):
        for item in self.itemsBox.items():
            if item not in self.redItems:
                item.setVisible(not self.filterButton.isChecked())
    
    def update(self):
        flag = False
        for widget in self.redItems:
            if widget.isChecked():
                node, newPath = self.referenceNodeAndPath(widget)
                be.change_ref(node, newPath)
                flag = True
        if flag: self.refresh()
    
    def refresh(self):
        self.clearItems()
        self.addItems()
        self.selectAllButton.setChecked(False)
        self.filterButton.setChecked(False)
        self.itemsBox.searchBox.clear()
    
    def closeEvent(self, event):
        self.deleteLater()
    
    def hideEvent(self, event):
        self.close()
        
    def button(self, icon):
        button = QCheckBox(self)
        button.setIcon(icon)
        return button

    def addScroller(self, title):
        scroller = cui.Scroller(self)
        scroller.setTitle(title)
        self.scrollerLayout.addWidget(scroller)
        return scroller