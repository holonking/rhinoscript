import rhinoscriptsyntax as rs
import Rhino
import scriptcontext
import System.Guid

import clr
clr.AddReference("Eto")
clr.AddReference("Rhino.UI")


from Rhino.UI import *
from Eto.Forms import Form, Dialog, Label, TextBox, StackLayout, StackLayoutItem, Orientation, Button, HorizontalAlignment, MessageBox
from Eto.Drawing import *
count=0
def handleAddObj():
    print ("objects updated, count:", count)
    count+=1

#main form
form=Form()
form.ClientSize=Size(200,200)


#components
label = Label()
label.Text = "onAddObject"

bt_addHandler=Button(Text="ADD")
bt_subHandler=Button(Text="SUB")

def addHandler_clicked(sender,e):
    Rhino.RhinoDoc.ActiveDoc.AddRhinoObject+=handleAddObj
def subHandler_clicked(sender,e):
    Rhino.RhinoDoc.ActiveDoc.AddRhinoObject-=handleAddObj

bt_addHandler.Click+=addHandler_clicked
bt_subHandler.Click+=subHandler_clicked


#Create layout and add to form
layH = StackLayout(Spacing = 5, Orientation = Orientation.Horizontal)
form.Content=layH


#add components to layout
# layH.Items.Add(label)
layH.Items.Add(bt_addHandler)
layH.Items.Add(bt_subHandler)

form.Show()


# obj = Dialog()
# obj.Title = "Some Dialog"
# obj.ClientSize = Size(200, 200)
# obj.Content = label

# obj.ShowModal(RhinoEtoApp.MainWindow)
# obj.ShowModalAsync()
