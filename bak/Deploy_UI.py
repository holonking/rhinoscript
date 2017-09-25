import System
import System.Windows.Forms as Forms
from System.Windows.Forms import *
import System.Drawing as Drawing
from System.Drawing import *
import Rhino
import rhinoscriptsyntax as rs
import os
import rsTools
reload(rsTools)
from rsTools import *


class MainForm(Forms.Form):
    def __init__(self):
        self.Size=Size(300,600)
        self.Closing += self.OnClosingEvent
        self.initUI()
        self.initEvents()

    def OnClosingEvent(self, sender, e):
        print('closing window form, remove handler')

    def initUI(self):
        self.tabControl=System.Windows.Forms.TabControl()
        self.tabControl.Size=self.Size
        self.Controls.Add(self.tabControl)
        # self.tabControl.Location=Point(0,0)
        #self.initSrfTypeTab()
        #self.initMeshGenTab()

        #########################
        #####  tabs #############
        #########################
        # self.page_srf_type=TabPage()
        # self.page_srf_type.Size=self.Size
        self.srf_type_UI=self.genSrfTypeRows(self,10)

        #
        # self.page_mesh_type=TabPage()
        # self.page_mesh_type.Size=self.Size

        # self.tabControl.Controls.Add(self.page_srf_type)
        # self.tabControl.Controls.Add(self.page_mesh_type)

    def initEvents(self):
        pass

    def isolateLayer(self,layerName):
        names=rs.LayerNames()
        for n in names:
            if n==layerName:
                layers=rs.LayerVisible(layerName,True)
            else:rs.LayerVisible(n,False)

    def genSrfTypeRows(self,control,total):
        srfTypeUI=AttrDict()
        srfTypeUI.bts1=[]
        srfTypeUI.bts2=[]
        srfTypeUI.combos=[]
        srfTypeUI.viewSrf=None
        srfTypeUI.viewMesh=None

        btVSrf=Button()
        btVSrf.Text='VSrf'
        btVSrf.Size=Size(100,30)
        btVSrf.Location=Point(0,0)

        btVMesh=Button()
        btVMesh.Text='VMesh'
        btVMesh.Size=Size(100,30)
        btVMesh.Location=Point(110,0)
        control.Controls.Add(btVSrf)
        control.Controls.Add(btVMesh)

        btRegenAll=Button()
        btRegenAll.Text='Regen'
        btRegenAll.Size=Size(30,30)
        btRegenAll.Location=Point(230,0)
        control.Controls.Add(btRegenAll)

        srfTypeUI.viewSrf=btVSrf
        srfTypeUI.viewMesh=btVMesh
        srfTypeUI.regenAll=btRegenAll

        for i in range(0,total):
            bt1,bt2,combo=self.genSrfTypeRow(i,control)
            srfTypeUI.bts1.append(bt1)
            srfTypeUI.bts2.append(bt2)
            srfTypeUI.combos.append(combo)
        return srfTypeUI

    def genSrfTypeRow(self,num,control):

        yoffset=50
        size=Size(30,30)
        size2=Size(180,15)
        h=35

        bt1=Button()
        bt1.Size=size
        bt1.Text=str(num)
        bt1.Location=Point(0,num*h+yoffset)

        bt2=Button()
        bt2.Text='SET'
        bt2.Size=size
        bt2.Location=Point(40,num*h+yoffset)

        combo=ComboBox()
        combo.Size=size2
        combo.Location=Point(80,num*h+yoffset)
        PATH='./FacadePatterns'
        files=[]
        for f in os.listdir(PATH):
            if '.facade' in f:
                files.append(f)
        print files
        count=len(files)

        arr=System.Array[object]
        combo.Items.AddRange(arr(files))
        if num<len(files):
            combo.SelectedIndex=int(num)

        control.Controls.Add(bt1)
        control.Controls.Add(bt2)
        control.Controls.Add(combo)

        return bt1,bt2,combo



#form = MainForm()
#form.TopMost=True
#form.Show()
