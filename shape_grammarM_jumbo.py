import rhinoscriptsyntax as rs
import RsTools.ShapeGrammarM as sg
reload(sg)
from Rhino.Geometry import *

sg.reset()

b=sg.create_box(Point3d(63,20,80),name='start')
sg.add_rhino_box('init',given_name='start')


sg.divide_z('start',[12,12,'r'],['even','odd','start'])
sg.divide_x('even',[9,9,9,'r'],['A','B','B','even'])
sg.divide_x('odd' ,[9,9,9,'r'],['B','A','A','odd'])

sg.scale_y('B',1.1,alignment=sg.Align.N)
sg.extract_face('B','S','B_S')
sg.import_component('component_cw_01','cw1')
sg.divide_face_uv('B_S',1.5,3,'B_S_bay')
sg.component_on_face('B_S_bay','cw1')
sg.end()
