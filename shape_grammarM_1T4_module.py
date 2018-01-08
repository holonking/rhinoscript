import rhinoscriptsyntax as rs
import RsTools.ShapeGrammarM as sg
from Rhino.Geometry import *

def T4(name,out_names=['f_ebed','f_sbed','f_lvg','f_bath']):
    #output:
    #f_ebed
    #f_sbed
    #f_lvg
    #f_bath
    s='a0dqwedsassdfsdf'
    sg.ADDSTEPS=False
    sg.enable_print_steps(False)
    sg.divide_z(name,[3,'r'],[s+'level',name])
    
    #massing
    sg.divide_my(s+'level',0.5,[s+'A',s+'B'])
    sg.divide_mx(s+'B',0.4,[s+'n',s+'core'])
    sg.move_ratio(s+'n',[0,0.5,0])
    sg.divide_mx(s+'A',0.5,[s+'s'])
    sg.scale_x(s+'s',0.5,sg.Align.E)

    
    #unit layouts
    sg.divide_x(s+'s',[0.5,0.5],[s+'ebed_s',s+'lvg'])
    sg.divide_x(s+'n',[0.3,0.3,0.4],[s+'ebed_n',s+'mbed',s+'lvg'])
    sg.divide_my(s+'ebed_n',0.4,[s+'ebed',s+'bath'])
    sg.divide_my(s+'ebed_s',0.5,[s+'ebed',s+'sbed'])
    sg.scale_y(s+'lvg',0.9)


    #facade details
    sg.extract_face(s+'ebed','S',out_names[0])
    sg.extract_face(s+'sbed','W',out_names[1])
    sg.extract_face(s+'lvg','S',out_names[2])
    sg.extract_face(s+'bath','W',out_names[3])


    sg.ADDSTEPS=True
    sg.enable_print_steps(True)
    sg.ENGINE.add_step('{} ->T4-> {}'.format(name,out_names))
    #output:
    #f_ebed
    #f_sbed
    #f_lvg
    #f_bath

def main():
    reload(sg)
    sg.reset()
    sg.create_box((36,25,80),name='start')
    T4('start',['f_ebed','f_sbed','f_lvg','f_bath'])
    sg.end()
    
if __name__ == '__main__':
    main()




