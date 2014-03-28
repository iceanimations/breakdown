from uiContainer import uic
from PyQt4.QtGui import *
import os.path as osp
import util
from customui import ui as cui
import pymel.core as pc

rootPath = osp.dirname(osp.dirname(__file__))
uiPath = osp.join(rootPath, 'ui')
iconPath = osp.join(rootPath, 'icons')

Form, Base = uic.loadUiType(osp.join(uiPath, 'breakdown.ui'))
class Breakdown(Form, Base):
    def __init__(self, parent=None):
        super(Breakdown, self).__init__(parent)
        self.setupUi(self)
        self.redIcon = QIcon(osp.join(iconPath, 'red.png'))
        self.greenIcon = QIcon(osp.join(iconPath, 'green.png'))
        self.itemsBox = self.addScroller('All References')
        self.redItems = []
        self.addItems()
        
    def addItems(self):
        refs = util.check_scene()
        item = self.createItem()
    
    def createItem(self, title, btn, subTitle='', thiredTitle='', detail=''):
        item = cui.Item(self)
        item.setTitle(title)
        item.setSubTitle(subTitle)
        item.setThirdTitle(thiredTitle)
        item.setDetail(detail)
        item.addWidget(btn)
        return item
    
    def clearItems(self):
        pass
    
    def selectAll(self):
        pass
        
    def handleSelectAllButton(self):
        pass
    
    def filterRed(self):
        pass
    
    def update(self):
        pass
    
    def refresh(self):
        pass
    
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
        scroller.setTitle('title')
        self.scrollerLayout.addWidget(scroller)
        return scroller