import sys

sys.path.append(r"c:\Program Files\Rhino WIP\System")
import clr

clr.AddReference("Eto")
clr.AddReference("Rhino.UI")
import Rhino
#from Rhino.UI import *
import Eto
import Eto.Forms as EForms
from Eto.Forms import Form, Panel, Dialog, Label, \
    TabControl, ComboBox, TabPage, TextBox, TextArea, \
    StackLayout, StackLayoutItem, Orientation, Button, \
    HorizontalAlignment, MessageBox, Slider

from Eto.Drawing import *

class RuleSlider(Slider):
    def __init__(self):
        super(RuleSlider,self).__init__()
        self.callbacks=[]

    def OnValueChanged(self, e):
        if self.callbacks:
            try:
                for callback in self.callbacks:
                    callback(self.Value)
            except Exception as e:
                print(e)

class NamePanel(Panel):
    def __init__(self):
        layV = StackLayout(Spacing=0, Orientation=Orientation.Vertical)
        self.layout=layV
        self.Content = layV
        self.Size=Size(70,600)
        self.button_size=Size(70,20)

    def add_name(self,name,color):
        bt = Button()
        bt.Text=name
        bt.Size=self.button_size
        bt.BackgroundColor = Color(color[0] / 255.0, color[1] / 255.0, color[2] / 255.0)
        self.layout.Items.Add(bt)
        return bt

class RuleRow(Panel):
    def __init__(self):
        layH = StackLayout(Spacing=0, Orientation=Orientation.Horizontal)
        self.bt_expand = Button()
        self.bt_expand.Size=Size(100,20)
        self.bt_expand.Text='EX'
        self.Content = layH
        layH.Items.Add(self.bt_expand)


class RulePanel(Panel):
    def __init__(self):
        layV = StackLayout(Spacing=0, Orientation=Orientation.Vertical)
        self.Size = Size(300, 600)
        self.Content = layV
        self.tb_rules = TextBox()
        self.tb_rules.Size = Size(300, 450)
        self.tb_rules.Text = 'asd'
        self.tb_guid = TextBox()
        self.tb_guid.Size=Size(300,20)
        self.tb_guid.Text='selected guid'
        self.slider = RuleSlider()
        self.slider.Size = Size(280, 100)
        self.slider.MinValue = 0
        layV.Items.Add(self.tb_rules)
        layV.Items.Add(self.tb_guid)
        layV.Items.Add(self.slider)

class RulePanel2(Panel):
    def __init__(self):
        layV = StackLayout(Spacing=0, Orientation=Orientation.Vertical)
        self.Size = Size(300, 600)
        self.Content = layV
        self.pn_rules = Panel()
        self.pn_rules.Size = Size(300, 450)
        self.pn_rules.Content=StackLayout(Spacing=0, Orientation=Orientation.Vertical)

        self.tb_guid = TextBox()
        self.tb_guid.Size=Size(300,20)
        self.tb_guid.Text='selected guid'
        self.slider = RuleSlider()
        self.slider.Size = Size(280, 100)
        self.slider.MinValue = 0
        layV.Items.Add(self.pn_rules)
        layV.Items.Add(self.tb_guid)
        layV.Items.Add(self.slider)
    def add_rule(self,name):
        self.pn_rules.Content.Items.Add(RuleRow())
        pass


class ShapeForm(Form):
    def __init__(self):
        layH = StackLayout(Spacing=0, Orientation=Orientation.Horizontal)
        self.Size=Size(500,600)
        self.rules=RulePanel()
        #RulePanel2 is reserved for interactive rule UI
        self.names=NamePanel()
        self.Content=layH

        layH.Items.Add(self.rules)
        layH.Items.Add(self.names)

    def show(self):
        self.Show()


