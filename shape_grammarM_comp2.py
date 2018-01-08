import rhinoscriptsyntax as rs
#from RsTools import *
#reload(MeshTools)
import RsTools.ShapeGrammarM as sg
reload(sg)
from Rhino.Geometry import *

sg.reset()
sg.start()

sg.add_rhino_box('com')
sg.add_rhino_box('office')
sg.add_rhino_box('apt')

#plinth
sg.divide_mx('com',0.1,['flank','main'])
sg.scale_y('flank',0.8,sg.Align.E)
sg.divide_mx('main',0.4,['sides','mid'])
sg.divide_my('mid',0.2,['m_en','inner'])
sg.scale_y('m_en',2,sg.Align.E)
sg.scale_z('m_en',1.1,sg.Align.E)

#offce tower
sg.rename('apt','office') 
sg.divide_z('office',[0.7,0.2,0.1],['ot1','ot2','ot3'])
sg.divide_mx('ot1',0.2,['ot1f','ot1m'])
sg.divide_x('ot1f',[0.5,0.5],['ot1fa','ot1fb'])
sg.scale_y('ot1fb',0.8,sg.Align.E)
sg.scale_y('ot1fa',0.6,sg.Align.E)

sg.divide_mx('ot2',0.1,['ot2f','ot2m'])
sg.scale_y('ot2m',0.8,sg.Align.E)
sg.scale_y('ot2f',0.6,sg.Align.E)
sg.scale_y('ot3',0.6,sg.Align.E)
sg.scale_x('ot3',0.8,sg.Align.S)



#environment
sg.duplicate('e_l1','egb')
sg.move_ratio('egb',[-1,0,0])

sg.duplicate('m_l1','mgb')
sg.move_ratio('mgb',[0,1,0])
sg.extract_face('mgb','B','mg')
sg.hide_name('mgb')

sg.end()