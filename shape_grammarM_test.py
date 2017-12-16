import rhinoscriptsyntax as rs
#from RsTools import *
#reload(MeshTools)
import RsTools.ShapeGrammarM as sg
reload(sg)
from Rhino.Geometry import *


sg.enable_redraw(False)
sg.clear_doc()
b=sg.create_box(Point3d(56,20,80),name='start')
sg.divide_z('start',[0.9,0.1],['bot','A'])
sg.scale_x('A',0.9,sg.Align.W)
sg.divide_x('bot',[0.2,0.8],['A','B'])
sg.scale_y('B',1.2,sg.Align.M)
sg.divide_x('B',[0.5,0.4,0.1],['C','D','E'])
sg.divide_y('D',[0.1,0.8,0.1],['bal','main'])
sg.divide_z('bal',[3,3,'r'],['D_odd','D_event','bal'])
sg.scale_y('D_odd',1.5)
sg.move('D_odd',[-5,0,0])

sg.set_z('D_odd',2)
sg.set_z('D_event',2)

sg.enable_redraw(True)

