import rhinoscriptsyntax as rs
import RsTools.ShapeGrammar as sg
reload(sg)
from Rhino.Geometry import *
eg=sg.ENGINE


rs.EnableRedraw(False)

eg.clear()
#eg.add_name('start')
eg.create_box_((20,56,60),'A')
objs=eg.get_by_name('A')
print(len(objs))
#eg.divide('A',[0.6,'r'],['B','A'],direction=1,delete_input=False)
eg.invert('A',2)
eg.divide('A',[3,'r'],['level','A'],direction=2,delete_input=False,ratio_mode=False)

eg.bisect_mirror('level',0.4,['flank','core'],direction=1)
eg.bisect_mirror('flank',0.5,['south','north'],direction=0)
eg.divide('south',[0.3,0.3,0.4],['B','C','D'],direction=1)
eg.divide('north',[0.3,0.3,0.4],['B','C','D'],direction=1)
eg.invert('B',0)
eg.invert('D',0)
eg.scale('D',[1.3,1,1],centered=False)
eg.scale('B',[1.1,1,1],centered=False)

eg.print_tree()


#eg.move('core',[1,0,0])

rs.EnableRedraw(True)

