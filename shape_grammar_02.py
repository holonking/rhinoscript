import rhinoscriptsyntax as rs
import RsTools.ShapeGrammar as sg
reload(sg)

sg.clear()
rs.EnableRedraw(False)

sg.divide_w('start',[0.4,0.6],  ['main','high'], False)
sg.divide_v('high', [0.4,0.6],  ['flow','main'])
sg.scale('flow',[1.2,1.2,1])
sg.divide_w('flow', [12,'r'],    ['level'], ratio_mode=False)
sg.divide_w('main', [6,'r'],    ['level2'], ratio_mode=False)

#pattern
#sg.divide_w('box_A', [0.05, 'r'], ['A_level_1','A_level_2'])
#sg.scale('A_level_2',[1.2,1.2,1])

rs.EnableRedraw(True)


