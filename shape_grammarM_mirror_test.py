import rhinoscriptsyntax as rs
import RsTools.ShapeGrammarM as sg
reload(sg)
from Rhino.Geometry import *

sg.reset()
sg.ENGINE.print_tree()
sg.create_box((54,25,80),name='start')
sg.divide_my('start',0.5,['A','B'])
sg.divide_mx('B',0.4,['n','core'])
sg.move_ratio('n',[0,0.5,0])
sg.divide_mx('A',0.5,['s'])
sg.scale_x('s',0.5,sg.Align.E)
sg.divide_x('s',[0.5,0.5],['lvg','bed'])
sg.divide_x('n',[0.3,0.3,0.4],['lvg','bed'])
sg.colorize()


sg.end()

