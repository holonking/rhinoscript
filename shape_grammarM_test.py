import rhinoscriptsyntax as rs
import RsTools.ShapeGrammarM as sg
reload(sg)
from Rhino.Geometry import *

eg=sg.Engine()
rs.EnableRedraw(False)
eg.clear_doc()

b=sg.create_box(Point3d(56,20,60),name='start')
sg.divide_x('start',[0.4,0.6],['B','A'])
sg.group(['B','A'],'group1')
sg.divide_z('group1',[3,'r'],['level'])


rs.EnableRedraw(True)

