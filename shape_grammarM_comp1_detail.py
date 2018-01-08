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
sg.divide_mx('com',0.35,['flank','mid'])
sg.divide_x('flank',[0.5,0.5],['A','B'])
sg.scale_y('A',1.2,sg.Align.E)
sg.scale_x('A',1.1,sg.Align.E)
sg.divide_y('A',[0.3,0.4,0.3],['corner','ent'])
sg.scale_z('corner',1.1,sg.Align.W)
sg.decompose_4('corner')
objs=sg.ENGINE.get_by_name('corner_S')
for o in objs:
    rs.SelectObject(o.guid)

sg.scale_y('mid',1.2,sg.Align.W)
sg.scale_z('mid',1.1,sg.Align.W)
sg.divide_z('mid',[5,'r'],['m_l1','m_main'])
sg.divide_z('B',[5,'r'],['f_l1','f_main'])
sg.divide_z('ent',[5,'r'],['e_l1','e_main'])

sg.scale_x('e_main',1.1,sg.Align.E)
sg.scale_x('e_l1',0.9,sg.Align.E)
sg.scale_y('f_l1',0.95,sg.Align.E)
sg.scale_y('m_l1',0.7,sg.Align.E)

#offce tower
sg.divide_my('office',0.5,['ot','otn'])
sg.invert_x('otn')
sg.scale_x('ot',0.9,sg.Align.E)
sg.scale_x('otn',0.9,sg.Align.E)
sg.divide_z('ot',[0.9,0.1],['otb','oth'])
sg.divide_z('otn',[0.9,0.1],['otb','othn'])
sg.scale_z('othn',2,'oth')

#apt
sg.divide_z('apt',[20,'r'],['apt_b','apt_t'])
sg.divide_z('apt_t',[0.7,0.2,0.1],['apt1','apt2','apt3'])
sg.scale_y('apt_b',0.95)
sg.scale_y('apt2',0.95)
sg.scale_y('apt3',0.6)
sg.decompose_2('apt1',['H','f_cw1'])
sg.decompose_2('apt2')


#environment
sg.duplicate('e_l1','egb')
sg.move_ratio('egb',[-1,0,0])
sg.extract_face('egb','B','eg')
sg.hide_name('egb')

sg.duplicate('m_l1','mgb')
sg.move_ratio('mgb',[0,1,0])
sg.extract_face('mgb','B','mg')
sg.hide_name('mgb')

#detail
sg.duplicate('otb','otbflr')
#sg.divide_z('otb',[4,'r'],['otl','otb'])
sg.decompose_4('otb')

sg.scale_x('otbflr',0.98,sg.Align.N)
sg.scale_y('otbflr',0.9,sg.Align.E)
sg.divide_z('otbflr',[4,'r'],['otb_floor','otbflr'])
sg.set_z('otb_floor',0.6)
sg.move_ratio('otb_floor',[0,0,-1])

sg.rename('otb_corner_S','srf_cw1')
sg.rename('otb_corner_N','srf_cw1')

sg.import_component('component_cw_03','cw1')

sg.divide_face_uv('otb_apt2_apt1_corner_S',1.5,4,'f_cw1',False)
sg.divide_face_uv('apt2_apt1_corner_S',3,4,'f_cw1')
sg.divide_face_uv('apt1_corner_S',1.5,4,'f_cw1')



sg.component_on_face('f_cw1','cw1')


sg.end()