import rhinoscriptsyntax as rs
import RsTools.ShapeGrammarM as sg

#sg.divide_z('otb_corner_SN',[4,'r'],['otb_level','otb_corner_SN'])

rs.EnableRedraw(False)
sg.import_component('component_cw_01','cw1')
sg.divide_face_uv('srf_cw1',1.5,4,'f_cw1',False)
sg.component_on_face('f_cw1','cw1')
rs.EnableRedraw(True)
