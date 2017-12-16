import sys

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



class ShapeForm(Form):
    def __init__(self):
        layV = StackLayout(Spacing=0, Orientation=Orientation.Vertical)
        self.Size=Size(300,600)
        self.Content = layV
        self.tb_rules=TextBox()
        self.tb_rules.Size=Size(300,500)
        self.tb_rules.Text='asd'
        self.slider=RuleSlider()
        self.slider.Size=Size(280,100)
        self.slider.MinValue=0
        layV.Items.Add(self.tb_rules)
        layV.Items.Add(self.slider)

