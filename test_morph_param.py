import rhinoscriptsyntax as rs
import Rhino.Geometry as rg
import Rhino
import RsTools.FormMorph as rtf
import RsTools.MorphUI as rtm
import RsTools.ShapeGrammar as sg
reload(rtm)
reload(rtf)
reload(sg)



sg.clear()
rs.EnableRedraw(False)

sg.divide_v('wa',   [0.4,0.2,0.4],  ['box_A','box_B'])
sg.scale('box_B',   [1,0.8,1])
sg.move('box_B',    [0,0.1/0.8,0])
sg.copy('box_B','treasure',[0,-0.5,0.4])
sg.scale('treasure',[1,1.5,0.5])

#pattern
#sg.divide_w('box_A', [0.05, 'r'], ['A_level_1','A_level_2'])
#sg.scale('A_level_2',[1.2,1.2,1])

rs.EnableRedraw(True)


