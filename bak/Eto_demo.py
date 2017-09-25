import rhinoscriptsyntax as rs
import Rhino
import Rhino.UI
import scriptcontext
import System.Guid

import clr
clr.AddReference("Eto")
clr.AddReference("Rhino.UI")



from Rhino.UI import *
from Eto.Forms import Form, Dialog, Label, TextBox, StackLayout, StackLayoutItem, Orientation, Button, HorizontalAlignment, MessageBox
from Eto.Drawing import *

dlg = Dialog[bool](Title = "Some Dialog", Padding = Padding(10))

label = Label(Text = "Enter a value:")
textBox = TextBox()

entry = StackLayout(Spacing = 5, Orientation = Orientation.Horizontal)
entry.Items.Add(label)
entry.Items.Add(textBox)

activate=Button (Text="Activiate")
def act_click(sender,e):print("hahaha")
activate.Click+=act_click

apply = Button(Text = "Apply")
def apply_click(sender, e): dlg.Close(True) # true is return value
apply.Click += apply_click

cancel = Button(Text = "Cancel")
def cancel_click(sender, e): dlg.Close(False)
cancel.Click += cancel_click

buttons = StackLayout(Spacing = 5, Orientation = Orientation.Horizontal)
buttons.Items.Add(activate)
buttons.Items.Add(cancel)
buttons.Items.Add(apply)


content = StackLayout(Spacing = 5) # default orientation is vertical
content.Items.Add(entry)
content.Items.Add(StackLayoutItem(buttons, HorizontalAlignment.Right))

dlg.DefaultButton = apply
dlg.AbortButton = cancel
dlg.Content = content
#dlg.Show()
 result = dlg.ShowModal(RhinoEtoApp.MainWindow)
# result=dlg.ShowSemiModal(RhinoEtoApp.MainWindow)
if result:
	# Do something
	MessageBox.Show("You entered: " + textBox.Text)
