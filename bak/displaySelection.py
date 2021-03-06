import System.Windows.Forms
from System.Windows import *
import Rhino
import rhinoscriptsyntax as rs

COUNTER=0

class HelloWorldForm(System.Windows.Forms.Form):
    def __init__(self):
        self.Text = 'Hello World'
        self.Name = 'Hello World'
        self.Closing += self.OnClosingEvent

        self.tb1=Forms.TextBox()
        self.tb1.Text='hello'

        self.initRhinoDoc()

    #//////////////////////////////
    #//// rhino event handlers ////
    #//////////////////////////////

    def handleAddObj(self,sender,e):
        global COUNTER
        print("print from RhinoDocEvent.py ",COUNTER)
        COUNTER+=1
        #rs.AddCircle((0,0,0),count

    def handleSelectObj(self,sender,e):
        sel=rs.SelectedObjects()
        print('handleSelectObj')
        if len(sel)==1:
            print('selected obj ID:',sel[0])

        else:
            print('selected multiple objs, len=',len(sel))
            for obj in sel:
                print('obj :',obj)
                isGroup=rs.IsGroup(obj)
                if isGroup:
                    print('group:',obj)
                    items=rs.ObjectsByGroup(obj)
                    for item in items:
                        print('item ',i,':',item)



    #////////////////////////////////////
    #//// assign rhino event handlers ///
    #////////////////////////////////////

    def initRhinoDoc(self):
        print('add event handler')
        Rhino.RhinoDoc.AddRhinoObject+=self.handleAddObj
        Rhino.RhinoDoc.SelectObjects+=self.handleSelectObj

    def OnClosingEvent(self, sender, e):
        print('closing window form, remove handler')
        Rhino.RhinoDoc.AddRhinoObject-=self.handleAddObj
        Rhino.RhinoDoc.SelectObjects-=self.handleSelectObj


form = HelloWorldForm()
form.TopMost=True
form.Show()
