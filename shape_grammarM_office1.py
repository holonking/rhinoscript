import rhinoscriptsyntax as rs
import RsTools.ShapeGrammarM as sg
reload(sg)
from Rhino.Geometry import *

sg.enable_redraw(False)
sg.clear_doc()
b=sg.create_box(Point3d(56,20,80),name='start')
sg.add_rhino_box('init',given_name='start')

sg.divide_x('start',[0.35,0.3,0.35],['flank','core'])
sg.duplicate('core','flow')
sg.scale_z('flow',0.5)
sg.scale_y('flow',0.8,alignment=sg.Align.S)
sg.move_ratio('flow',[0,-0.2,1.2])
sg.scale_y('core',0.8,alignment=sg.Align.N)
sg.enable_redraw(True)

