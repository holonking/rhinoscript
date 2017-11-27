import rhinoscriptsyntax as rs
import Rhino.Geometry as rg
import Rhino
import RsTools.FormMorph as rtf
import RsTools.MorphUI as rtm
reload(rtm)
reload(rtf)


from Rhino.Geometry import *
sel=rs.ObjectsByName('subject')
brepid=sel[0]

shape=rtm.Shape1()
shape.set_box(brepid)
shape.show_params()