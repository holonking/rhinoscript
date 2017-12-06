import rhinoscriptsyntax as rs
import RsTools.ShapeGrammar as sg
reload(sg)
from Rhino.Geometry import *
eg=sg.ENGINE


rs.EnableRedraw(False)

eg.clear()
eg.add_name('start')



eg.divide('node',[0.35,0.3,0.35],['flank','core'],direction=1,delete_input=False)
eg.copy('core','flow')
eg.divide('core',[0.2,0.8],['garden','core'],direction=0)
eg.scale('flow',[0.8,1,0.5],centered=False)
eg.move('flow',[-1/4,0,1.1])

eg.delete_name('garden')
rs.EnableRedraw(True)
