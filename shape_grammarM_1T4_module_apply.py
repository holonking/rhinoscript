import rhinoscriptsyntax as rs
from Rhino.Geometry import *
import RsTools.ShapeGrammarM as sg
reload(sg)
from shape_grammarM_1T4_module import T4

sg.reset()

#form
#sg.create_box((34,25,18),name='start')
sg.add_rhino_box('resid','start')
T4('start',['f_ebed','f_sbed','f_lvg','f_bath'])

#load components
for i in range(4):
    s=str(i+1)
    sg.import_component('component_rs_bed_0'+s,'cw'+s)
    sg.import_component('component_rs_bed_0'+s,'cw'+s)

sg.import_component('component_rs_lvg_01','cw5')

#apply facade
#sg.draw_axies('f_ebed')
sg.component_on_face('f_ebed','cw4')
sg.component_on_face('f_sbed','cw2')
sg.component_on_face('f_lvg','cw5')

sg.component_on_face('f_ebed','cw1')
sg.component_on_face('f_ebed','cw2')
sg.component_on_face('f_ebed','cw3')
sg.component_on_face('f_ebed','cw5')
sg.end()