import Rhino
import rhinoscriptsyntax as rs

#
# import Deploy_BaseTypes
# reload(Deploy_BaseTypes)
# from Deploy_BaseTypes import *

import Deploy_Engine
reload(Deploy_Engine)
from Deploy_Engine import Engine

import Deploy_ETOUI
reload(Deploy_ETOUI)
from Deploy_ETOUI import MainForm

# import Deploy_ETO_AssignActions
# reload(Deploy_ETO_AssignActions)
# from Deploy_ETO_AssignActions import *

import clr
clr.AddReference("Eto")
clr.AddReference("Rhino.UI")

# from Rhino.UI import *
# from Eto.Forms import Form, Dialog, Label, TabControl, ComboBox,TabPage, TextBox, StackLayout, StackLayoutItem, Orientation, Button, HorizontalAlignment, MessageBox
# from Eto.Drawing import *

engine=Engine()
#engine.fixCurrentModel()
form = MainForm()
form.initUI(engine)
form.TopMost=True

try:
    engine.assignAction(form)
except Exception as e:print(e)
form.Show()
