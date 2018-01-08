import sys
import rhinoscriptsyntax as rs
sys.path.append(r"c:\Program Files\Rhino WIP\System")
import clr
clr.AddReference("Eto")
clr.AddReference("Rhino.UI")

from Rhino.UI import *
import Eto
import Eto.Forms as EForms
from Eto.Forms import Form, Panel, Dialog, Label, \
    TabControl, ComboBox, TabPage, TextBox, TextArea, \
    StackLayout, StackLayoutItem, Orientation, Button, \
    HorizontalAlignment, MessageBox, Slider
    
from RsTools import ShapeGrammarM as sg
try:
    #load components
    sg.import_component('component_rs_bed_04','cw1')
    sg.import_component('component_rs_bed_01','cw2')
    sg.import_component('component_rs_bed_02','cw3')
    sg.import_component('component_rs_bed_03','cw4')
    
    sg.import_component('component_rs_lvg_01','cw5')
    sg.import_component('component_rs_lvg_02','cw6')
    sg.import_component('component_rs_lvg_03','cw7')
    sg.import_component('component_rs_lvg_04','cw8')
    rs.EnableRedraw(False)
    rs.ENABLEREDRAW=False
    for i in [1,2,3,4]:
        print(i)
        s=str(i)
        s2=str(i+4)
        sg.component_on_face('f_ebed','cw'+s,'g_comp_b'+s)
        sg.component_on_face('f_lvg','cw'+s2,'g_comp_l'+s2)
    if i<4:
        sg.unstage('g_comp_b'+s)
        sg.unstage('g_comp_l'+s2)
    
    rs.ENABLEREDRAW=True
    rs.EnableRedraw(True)
    sg.ui.Show()
    
except Exception as e:
    print(e)
    pass