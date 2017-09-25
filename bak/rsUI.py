import System.Windows.Forms as Forms
from System.Windows.Forms import *

import System.Drawing as Drawing
from System.Drawing import *

import Rhino
import rhinoscriptsyntax as rs

class UI_tool_select(Panel):
    def __init__(self,parent=None,location=None):
        #super(self.__class__,self).__init__()

        self.parent=parent
        self.Size=Size(180,100)
        self.createUI()
        self.loadBehaviors()

        if parent is not None:
            parent.Controls.Add(self)
        if location is not None:
            self.Location=location

    def createUI(self):
        #create button1
        self.bt=Button()
        self.bt.Size=Size(50,15)
        self.bt.Text='select'
        self.bt.Location=Point(5,20)

        #create text Panel
        self.tb=TextBox()
        self.tb.Size=Size(100,15)
        self.tb.Text='empty'
        self.tb.Location=Point(65,26)

        self.Controls.Add(self.bt)
        self.Controls.Add(self.tb)


    def loadBehaviors(self):
        self.bt.Click+=self.handleClick

    def handleClick(self,sender,e):
        print('button clicked')
