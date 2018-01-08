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
sg.import_component('component_rs_bed_04','cw1')
sg.import_component('component_rs_bed_01','cw2')
sg.import_component('component_rs_bed_02','cw3')
sg.import_component('component_rs_bed_03','cw4')

sg.import_component('component_rs_lvg_01','cw5')
sg.import_component('component_rs_lvg_02','cw6')
sg.import_component('component_rs_lvg_03','cw7')
sg.import_component('component_rs_lvg_04','cw8')

#apply facade
for i in [1,2,3,4]:
        print(i)
        s=str(i)
        s2=str(i+4)
        sg.component_on_face('f_ebed','cw'+s,'g_comp_b'+s)
        sg.component_on_face('f_lvg','cw'+s2,'g_comp_l'+s2)
sg.end()