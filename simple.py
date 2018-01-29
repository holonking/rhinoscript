import rhinoscriptsyntax as rs
import RsTools.ShapeGrammarM as sg
from Rhino.Geometry import Vector3d
reload(sg)
from Rhino.Geometry import *

sg.reset()
sg.create_box(Vector3d(30,20,40),name='init')
sg.divide_x('init',[0.4,0.6],['A','B'])
sg.divide_z('B',[0.4,0.6],['C','D'])
sg.rename('A','D')
sg.divide_y('D',[0.5,0.5],['E'])
sg.end()

eg=sg.ENGINE
for o in eg.data:
    if o._parent is None:
        o.print_tree()
