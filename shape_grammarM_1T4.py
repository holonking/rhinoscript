import rhinoscriptsyntax as rs
import RsTools.ShapeGrammarM as sg
reload(sg)
from Rhino.Geometry import *

sg.reset()
sg.enable_print_steps(False)

def gen():
    sg.ENGINE.print_tree()
    #sg.create_box((32,20,18),name='start')
    #sg.add_rhino_box('init','start')
    sg.add_rhino_box('low','start')
    sg.divide_z('start',[3,'r'],['level','start'])
    sg.group(['foot','body'],'g1')
    sg.divide_x('g1',[0.5,0.5],'div')

    #massing
    sg.divide_my('level',0.5,['A','B'])
    sg.divide_mx('B',0.4,['n','core'])
    sg.move_ratio('n',[0,0.5,0])
    sg.divide_mx('A',0.5,['s'])
    sg.scale_x('s',0.5,sg.Align.E)
    
    #unit layouts
    sg.divide_x('s',[0.5,0.5],['ebed_s','lvg'])
    sg.divide_x('n',[0.3,0.3,0.4],['ebed_n','mbed','lvg'])
    sg.divide_my('ebed_n',0.4,['ebed','bath'])
    sg.divide_my('ebed_s',0.5,['ebed','sbed'])
    sg.scale_y('lvg',0.9)
    
    #load components
    sg.import_component('component_rs_bed_04','cw1')
    sg.import_component('component_rs_bed_01','cw2')
    
    #facade details
    sg.extract_face('ebed','S','f_ebed')
    sg.extract_face('sbed','W','f_sbed')
    #sg.draw_axies('f_ebed')
    sg.component_on_face('f_ebed','cw1')
    sg.component_on_face('f_sbed','cw2')

gen()


sg.end()

