import System
import System.Windows.Forms as Forms
from System.Windows.Forms import *
import System.Drawing as Drawing
from System.Drawing import *
import Rhino
import rhinoscriptsyntax as rs
import os
from os import path

import rsUI
reload(rsUI)
from rsUI import *

import rsTools
reload(rsTools)
from rsTools import *


class HelloWorldForm(Forms.Form):
    def __init__(self):
        self.Text = 'Hello World'
        self.Name = 'Hello World'
        self.Size=Size(200,350)
        self.Closing += self.OnClosingEvent
        self.initUI()

    def OnClosingEvent(self, sender, e):
        print('closing window form, remove handler')

    def initUI(self):
        print('init UI')
        self.SuspendLayout()

        selTool_crv=UI_tool_select(self,Point(5,20))

        combo=Forms.ComboBox()
        combo.Size=Size(150,20)
        combo.Location=Point(5,80)

        PATH='/Users/holonking/Documents/Design/RhinoComponents'
        #PATH='.'
        files=[]
        for f in os.listdir(PATH):
            if '.3dm' in f:
                files.append(f)

        print files
        count=len(files)
        arr=System.Array[object]

        combo.Items.AddRange(arr(files))
        self.Controls.Add(combo)
        #listBox.Items.add(f)

        #self.Controls.Add(listBox)

        task=applyComponent(selTool_crv,combo)

        self.ResumeLayout(False)
        # self.Controls.Add(tb)

form = HelloWorldForm()
form.TopMost=True
form.Show()
