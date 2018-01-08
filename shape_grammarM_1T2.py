import rhinoscriptsyntax as rs
import RsTools.ShapeGrammarM as sg
reload(sg)
from Rhino.Geometry import *

sg.reset()

def gen():
    #sg.ENGINE.print_tree()
    #sg.create_box((32,20,18),name='start')
    sg.add_rhino_box('resid','start')
    sg.scale_x('start',1.1,sg.Align.S)
    sg.scale_y('start',0.9,sg.Align.E)
    #sg.invert_('start',2)
    sg.divide_z('start',[3,'r'],['level','start'])
    
    sg.divide_mx('level',0.43,['flank','core'])
    sg.divide_my('flank',0.5,['south','north'])
    sg.divide_x('south',[0.3,0.3,0.4],['B','C','D'])
    sg.divide_x('north',[0.3,0.3,0.4],['B','C','D'])
    
    #sg.invert_x('B')
    sg.invert_x('D')
    sg.scale_y('D',0.9)
    sg.scale_y('B',0.8)
    
    sg.extract_face('D','S','f_lvg')
    sg.extract_face('B','S','f_ebed')
    sg.extract_face('C','S','f_sbed')

    #load components
    sg.import_component('component_rs_bed_04','cw1')
    sg.import_component('component_rs_bed_01','cw2')
    sg.import_component('component_rs_lvg_01','cw3')
    
    #apply facade
    #sg.draw_axies('f_ebed')
    sg.component_on_face('f_ebed','cw1')
    sg.component_on_face('f_sbed','cw2')
    sg.component_on_face('f_lvg','cw3')

gen()


sg.end()

