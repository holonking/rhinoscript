import rhinoscriptsyntax as rs
from Rhino.Geometry import *
import RsTools.ShapeGrammarM as sg
reload(sg)
from shape_grammarM_1T4_module import T4

sg.reset()

#form
sg.create_box((34,25,18),name='start')
T4('start',['f_ebed','f_sbed','f_lvg','f_bath'])

#load components
sg.import_component('component_rs_bed_04','cw1')
sg.import_component('component_rs_bed_01','cw2')
sg.import_component('component_rs_lvg_01','cw3')

#apply facade
#sg.draw_axies('f_ebed')
sg.component_on_face('f_ebed','cw1')
sg.component_on_face('f_sbed','cw2')
sg.component_on_face('f_lvg','cw3')
sg.end()