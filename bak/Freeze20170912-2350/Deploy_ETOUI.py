import rhinoscriptsyntax as rs
import Rhino
import scriptcontext
import System.Guid

import clr
clr.AddReference("Eto")
clr.AddReference("Rhino.UI")
from Rhino.UI import *
from Eto.Forms import Form, Dialog, Label, TabControl, ComboBox, TabPage, TextBox, StackLayout, StackLayoutItem, Orientation, Button, HorizontalAlignment, MessageBox
from Eto.Drawing import *
import os
import rsTools
reload(rsTools)
from rsTools import *


class MainForm(Form):
    def __init__(self):
        #super(Form,self).__init__(*args, **kwargs)
        # Form.Resizable=True
        self.Size=Size(300,600)
        #call initUI from outside and pass an engine to it
        #self.initUI()


    def initUI(self,engine):
        self.engine=engine
        tabControl=TabControl()
        layMain=StackLayout(Spacing = 2, Orientation = Orientation.Vertical)


        #control groups

        self.page_GENBLOCK=None
        self.page_GENMASSING=None
        self.page_GENTYPESRF=TabPage()
        self.page_GENTYPESRF.Text='SRF'
        self.page_GENTYPEMESH=TabPage()
        self.page_GENTYPEMESH.Text='MSH'
        self.page_GENCOMPONENT=None

        tabControl.Pages.Add(self.page_GENTYPESRF)
        tabControl.Pages.Add(self.page_GENTYPEMESH)

        self.Content=tabControl
        self.gen_GENTYPESRF_row()

    def gen_GENTYPESRF_row(self):
        layV=StackLayout(Spacing = 2, Orientation = Orientation.Vertical)
        layH1=StackLayout(Spacing = 0, Orientation = Orientation.Horizontal)
        self.UI_GENTYPESRF=AttrDict()

        bt_view_srf=Button()
        bt_view_srf.Text='viewSrf'
        bt_view_mesh=Button()
        bt_view_mesh.Text='viewMesh'
        bt_regen=Button()
        bt_regen.Text='Regen'
        bt_inspect=Button()
        bt_inspect.Text=('INSPECT')

        self.UI_GENTYPESRF.bt_view_srf=bt_view_srf
        self.UI_GENTYPESRF.bt_view_mesh=bt_view_mesh
        self.UI_GENTYPESRF.bt_regen=bt_regen
        self.UI_GENTYPESRF.bt_inspect=bt_inspect


        layH1.Items.Add(bt_view_srf)
        layH1.Items.Add(bt_view_mesh)
        layH1.Items.Add(bt_regen)
        layH1.Items.Add(bt_inspect)

        layV.Items.Add(layH1)

        self.UI_GENTYPESRF.bts1=[]
        self.UI_GENTYPESRF.bts2=[]
        self.UI_GENTYPESRF.combos=[]

        for i in range(0,10):
            row=AttrDict()
            layH=StackLayout(Spacing = 0, Orientation = Orientation.Horizontal)
            layV.Items.Add(layH)
            bt1=Button()
            bt1.Width=50
            bt1.Text=str(i)
            color=self.engine.get_SRFTYPECOLOR(i)
            print(color)
            bt1.BackgroundColor=Color(color[0],color[1],color[2])
            bt2=Button()
            bt2.Width=50
            bt2.Text='set'
            combo=ComboBox()
            combo.Width=150
            PATH=self.engine.getPathPattern()
            files=[]
            for f in os.listdir(PATH):
                if '.facade' in f:
                    files.append(f)
                    combo.Items.Add(f)
            print files
            count=len(files)

            # arr=System.Array[object]
            # combo.Items.AddRange(arr(files))
            if i<len(files):
                combo.SelectedIndex=i

            layH.Items.Add(bt1)
            layH.Items.Add(bt2)
            layH.Items.Add(combo)

            #update self.UI_*
            self.UI_GENTYPESRF.bts1.append(bt1)
            self.UI_GENTYPESRF.bts2.append(bt2)
            self.UI_GENTYPESRF.combos.append(combo)

        self.page_GENTYPESRF.Content=layV
