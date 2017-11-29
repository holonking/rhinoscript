import rhinoscriptsyntax as rs
import RsTools.ShapeGrammar as sg
reload(sg)
eg=sg.ENGINE


rs.EnableRedraw(False)

eg.clear()
eg.add_name('start')

eg.bisect_mirror('start',0.4,['flank','core'],direction=1,delete_input=False)
eg.divide('flank',[0.8,0.2],['A','B'],direction=1)
eg.print_tree()


#eg.move('core',[1,0,0])

rs.EnableRedraw(True)

