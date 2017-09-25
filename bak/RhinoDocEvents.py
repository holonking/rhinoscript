import rhinoscriptsyntax as rs
import Rhino

#the following is not working
def handleAddObj(sender,e):
    print("print from RhinoDocEvent.py")
    count+=1
    rs.AddCircle((0,0,0),count)
Rhino.RhinoDoc.ActiveDoc.AddRhinoObject+=handleAddObj
#Rhino.RhinoDoc.AddRhinoObject+=handleAddObj
