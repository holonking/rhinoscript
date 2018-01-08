import rhinoscriptsyntax as rs
import RsTools.ShapeGrammarM as sg
reload(sg)
from Rhino.Geometry import *

sg.reset()
#sg.create_box((20,10,40),name='S')
sg.add_rhino_box('resid','S')
sg.divide_my('S',0.5,['s','n'])
sg.divide_x('n',[0.4,0.6],['A','B'])
sg.divide_mx('n',0.4,['flank','core'])
sg.divide_mx('s',0.4,['f1','core','f2'])
sg.scale_x('f1',0.5,sg.Align.N)
sg.scale_y('f2',0.5,sg.Align.N)
sg.end()
