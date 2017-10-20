
# -*- coding: utf-8 -*-
import rhinoscriptsyntax as rs
import Rhino
import scriptcontext
import System.Guid

import clr
clr.AddReference("Eto")
clr.AddReference("Rhino.UI")
from Rhino.UI import *
from Eto.Forms import Form,Panel,Dialog, Label, TabControl,ComboBox, TabPage, TextBox, TextArea,StackLayout,StackLayoutItem, Orientation, Button,HorizontalAlignment, MessageBox
from Eto.Drawing import *
import os
import rsTools
reload(rsTools)
from rsTools import *


def Gen_title_combo_row(txt,items,return_all_controls=False):
    rowLayH=StackLayout(Spacing=0,Orientation=Orientation.Horizontal)
    title=Label()
    title.Size=Size(50,30)
    title.Text=txt
    combo=ComboBox()
    combo.Width=130
    for i in items:
        combo.Items.Add(str(i))
    combo.SelectedIndex=0
    rowLayH.Items.Add(title)
    rowLayH.Items.Add(combo)
    if return_all_controls:
        return rowLayH,title,combo
    else: return rowLayH
def Gen_title_bts_row(txt='txt',button_texts=['bt'],items=[1,2,3],
                        button_widths=[50],
                        return_all_controls=False):
    #TODO:generate StackLayout(horizontal) for this row
    pass


class DataPainter(Panel):

    def OnPaint(self,e):
        print('from DataPainter.OnPaint:',e)
    def MouseDown(self,e):
        print('from DataPainter.MouseDOwn:',e)


class MainForm(Form):
    def __init__(self):
        #super(Form,self).__init__(*args, **kwargs)
        # Form.Resizable=True
        self.Size=Size(550,600)
        #call initUI from outside and pass an engine to it
        #self.initUI()


    def initUI(self,engine):
        #┌────layMainH───┬───────────┐
        #│┌───layMainV──┐│treeTextBox│
        #││   tabPanel  ││           │
        #│├─────────────┤│           │
        #││  objTextBox ││           │
        #│├─────────────┤│           │
        #││  rhiTextBox ││           │
        #│└─────────────┘│           │
        #└───────────────┴───────────┘
        self.engine=engine
        tabControl=TabControl()
        layMainH=StackLayout(Spacing=0,Orientation=Orientation.Horizontal)
        layMainV=StackLayout(Spacing = 2, Orientation = Orientation.Vertical)

        layMainH.Items.Add(layMainV)

        #tab panel groupd
        self.tabPanel=Panel()
        self.tabPanel.Size=Size(200,350)
        self.page_GENBLOCK=TabPage()
        self.page_GENBLOCK.Text='BLK'
        self.page_GENTYPESRF=TabPage()
        self.page_GENTYPESRF.Text='SRF'
        self.page_GENTYPEMESH=TabPage()
        self.page_GENTYPEMESH.Text='MSH'
        self.page_GENCOMPONENT=None
        tabControl.Pages.Add(self.page_GENBLOCK)
        tabControl.Pages.Add(self.page_GENTYPESRF)
        tabControl.Pages.Add(self.page_GENTYPEMESH)
        self.tabPanel.Content=tabControl
        self.tabControl=tabControl

        self.page_GENTYPESRF.Content=self.gen_GENTYPESRF_row()
        self.page_GENTYPEMESH.Content=self.gen_GENTYPESRF_row()

        #objPanel
        self.objTextBox=TextBox()
        self.objTextBox.Size=Size(200,150)
        self.objTextBox.Text='phase obj \ninsoection'
        #rhiPanel
        self.rhiTextBox=TextBox()
        self.rhiTextBox.Size=Size(200,50)
        self.rhiTextBox.Text='rhino guid'

        layMainV.Items.Add(self.tabPanel)
        layMainV.Items.Add(self.objTextBox)
        layMainV.Items.Add(self.rhiTextBox)

        textBox=TextBox()
        textBox.Font=Font(textBox.Font.Typeface, 8);
        textBox.Size=Size(300,600)
        self.treeTextBox=textBox
        layMainH.Items.Add(textBox)

        self.Content=layMainH
        self.gen_GENBLOCK()
        self.gen_GENTYPESRF_row()

        self.gen_TOOLBAR(layMainH)

    def gen_GENBLOCK(self):
        layV=StackLayout(Spacing = 2, Orientation = Orientation.Vertical)
        layH=StackLayout(Spacing = 0, Orientation = Orientation.Horizontal)

        # bt_view_block=Button()
        # bt_view_block.Text='viewBlock'
        # bt_view_srf=Button()
        # bt_view_srf.Text='viewSrf'
        bt_interact=Button()
        bt_interact.Text='+Intr'


        self.UI_GENBLOCK=AttrDict()
        # self.UI_GENBLOCK.bt_view_block=bt_view_block
        # self.UI_GENBLOCK.bt_view_srf=bt_view_srf
        self.UI_GENBLOCK.bt_interact=bt_interact

        # layH.Items.Add(bt_view_block)
        # layH.Items.Add(bt_view_srf)
        layH.Items.Add(bt_interact)

        layV.Items.Add(layH)

        #TODO:add UI to set massing block properties
        #TODO:gen the row
        lb_selected_block=Label()
        lb_selected_block.Text='selected short guid'
        lb_selected_block.Width=100
        row_typeIndex,tempTitle,combo1=Gen_title_combo_row('w type1',range(10),True)
        row_typeIndex2,tempTitle,combo1b=Gen_title_combo_row('w type2',range(10),True)
        row_top_typeIndex,tempTitle,comboTop=Gen_title_combo_row('g type',range(10),return_all_controls=True)
        layV.Items.Add(lb_selected_block)
        layV.Items.Add(row_typeIndex)
        layV.Items.Add(row_typeIndex2)
        layV.Items.Add(row_top_typeIndex)

        self.UI_GENBLOCK.lb_selected_block=lb_selected_block
        self.UI_GENBLOCK.combo_typeIndex1=combo1
        self.UI_GENBLOCK.combo_typeIndex2=combo1b
        self.UI_GENBLOCK.combo_typeTopIndex=comboTop

        self.page_GENBLOCK.Content=layV

    def gen_TOOLBAR(self,layout):
        layV=StackLayout(Spacing = 2, Orientation = Orientation.Vertical)
        bt_width=30
        bt_delete=Button()
        bt_delete.Text='del'
        bt_delete.Width=bt_width

        layV.Items.Add(bt_delete)
        self.UI_TOOLBAR=AttrDict()
        self.UI_TOOLBAR.bt_delete=bt_delete

        layout.Items.Add(layV)

    def gen_GENTYPESRF_row(self):
        layV=StackLayout(Spacing = 2, Orientation = Orientation.Vertical)
        layH1=StackLayout(Spacing = 0, Orientation = Orientation.Horizontal)
        self.UI_GENTYPESRF=AttrDict()

        bt_view_srf=Button()
        bt_view_srf.Text='vSrf'
        bt_view_srf.Width=50
        bt_view_mesh=Button()
        bt_view_mesh.Text='vMesh'
        bt_view_mesh.Width=50
        bt_regen=Button()
        bt_regen.Text='Regen'
        bt_regen.Width=50
        bt_inspect=Button()
        bt_inspect.Text=('INSPECT')
        bt_inspect.Width=50

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
            bt1.Width=30
            bt1.Text=str(i)

            color=self.engine.get_color_set1(i)
            #print (color)
            #print(color)
            try:
                bt1.BackgroundColor=Color(color[0]/255.0,color[1]/255.0,color[2]/255.0)
            except:pass
            bt2=Button()
            bt2.Width=30
            bt2.Text='set'
            combo=ComboBox()
            combo.Width=140
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

        return layV
        #self.page_GENTYPESRF.Content=layV
