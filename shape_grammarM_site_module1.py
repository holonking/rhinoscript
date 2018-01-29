import rhinoscriptsyntax as rs
import RsTools.ShapeGrammarM as sg
#reload(sg)
from Rhino.Geometry import *

def SiteR1(name,out_names=['high','mid','low','flat','com']):
    s='a0dqwedsadsadssdfsf'
    #sg.ADDSTEPS=False
    #sg.enable_print_steps(False)
    
    p1=0.2
    ratio_com=0.2
    ratio_house=0.3
    ratio_tower=0.5
    ratio=[ratio_com,ratio_house,ratio_tower]
    sg.divide_mx(name,p1,[s+'flank',s+'mid'])
    sg.divide_mx(s+'mid',0.1,[s+'blv',s+'mid'])
    sg.divide_y(s+'flank',ratio,[s+'fk_com',s+'fk_hus',s+'fk_twr'])
    sg.divide_y(s+'mid',ratio,[s+'md_com',s+'md_hus',s+'md_twr'])
    
    #commercial
    sg.divide_x(s+'fk_com',[0.5,0.5],[s+'com1',s+'com_d'])
    sg.divide_y(s+'com_d',[0.5,0.5],[s+'com2',s+'gnd'])
    sg.divide_y(s+'md_com',[0.5,0.5],[s+'com3',s+'gnd'])
    sg.duplicate(s+'com1',s+'bdg_com1')
    sg.duplicate(s+'com2',s+'bdg_com2')
    sg.duplicate(s+'com3',s+'bdg_com3')
    sg.duplicate(s+'com3',s+'bdg_com4')
    sg.set_z(s+'bdg_com1',20)
    sg.set_z(s+'bdg_com2',15)
    sg.set_z(s+'bdg_com3',10)
    sg.set_z(s+'bdg_com4',20)
    sg.move_ratio(s+'bdg_com3',[0,-0.3,0])
    sg.scale_x(s+'bdg_com4',0.7,sg.Align.S)
    sg.scale_y(s+'bdg_com2',0.8,sg.Align.N)
    sg.rename(s+'bdg_com1','com')
    sg.rename(s+'bdg_com2','com')
    sg.rename(s+'bdg_com3','com')
    sg.rename(s+'bdg_com4','com')
    
    #house'
    sg.divide_y(s+'md_hus',[0.6,0.4],[s+'hus',s+'garden'])
    sg.extract_face(s+'hus','T','lnd_hus')
    sg.extract_face(s+'fk_hus','T','lnd_hus')
    sg.divide_face_uv('lnd_hus',30,30,'ulnd_hus')
    sg.box_on_face_center('ulnd_hus',25,18,12,'bdg_hus')


    
    #tower
    sg.divide_y(s+'md_twr',[0.5,0.5],[s+'mid',s+'high'])
    sg.divide_y(s+'fk_twr',[0.33,0.33,0.33],[s+'lnd_twr'])
    sg.extract_face(s+'mid','T','lnd_mid')
    sg.extract_face(s+'lnd_twr','T','ulnd_mid')
    sg.extract_face(s+'high','T','lnd_high')
    
    sg.divide_face_uv('lnd_mid',60,60,'ulnd_mid')
    sg.divide_face_uv('lnd_high',40,80,'ulnd_high')
    
    sg.box_on_face_center('ulnd_mid',30,20,60,'bdg_mid')
    sg.box_on_face_center('ulnd_high',30,20,99,'bdg_high')
    sg.move_ratio('bdg_mid',[0,-0.5,0])
    
    #////////////// SCULPT /////////////////////////
    #----house-------------------------------------------
    sg.divide_mx('bdg_hus',0.5,['half_hus'])
    sg.divide_x('half_hus',[0.5,0.5],['hus2','hus'])
    sg.scale_z('hus2',0.6)
    sg.scale_y('hus2',0.5)
    sg.rename('hus2','hus')
    sg.divide_z('hus',[3.5,'r'],['hus_level','hus'])
    
    #----1T4------------------------------------------
    sg.divide_z('bdg_mid',[3,'r'],['level','bdg_mid'])
    sg.group(['foot','body'],'g1')
    sg.divide_x('g1',[0.5,0.5],'div')

    sg.divide_my('level',0.5,['A','B'])
    sg.divide_mx('B',0.4,['n','core'])
    sg.move_ratio('n',[0,0.5,0])
    sg.divide_mx('A',0.5,['s'])
    sg.scale_x('s',0.5,sg.Align.E)

    sg.divide_x('s',[0.5,0.5],['ebed_s','lvg'])
    sg.divide_x('n',[0.3,0.3,0.4],['ebed_n','mbed','lvg'])
    sg.divide_my('ebed_n',0.4,['ebed','bath'])
    sg.divide_my('ebed_s',0.5,['ebed','sbed'])
    sg.scale_y('lvg',0.9)
    #----1T4------------------------------------------
    
    #----1T2------------------------------------------
    sg.scale_x('bdg_high',1.1,sg.Align.S)
    sg.scale_y('bdg_high',0.9,sg.Align.E)
    sg.divide_z('bdg_high',[3,'r'],['level','bdg_high'])
    
    sg.divide_mx('level',0.43,['flank','core'])
    sg.divide_my('flank',0.5,['south','north'])
    sg.divide_x('south',[0.3,0.3,0.4],['B','C','D'])
    sg.divide_x('north',[0.3,0.3,0.4],['B','C','D'])
    
    #sg.invert_x('B')
    sg.invert_x('D')
    sg.scale_y('D',0.9)
    sg.scale_y('B',0.8)
    #-----------1T2--------------------------------
    #facade details
    sg.extract_face('ebed','S','f_ebed')
    sg.extract_face('sbed','W','f_sbed')
    sg.extract_face('lvg','S','f_lvg')
    sg.extract_face('bath','W','f_bath')
    
    #load components
    sg.import_component('component_rs_bed_04','cw1')
    sg.import_component('component_rs_bed_01','cw2')
    sg.import_component('component_rs_lvg_01','cw3')
    
    #apply facade
    #sg.draw_axies('f_ebed')
    sg.component_on_face('f_ebed','cw1')
    sg.component_on_face('f_sbed','cw2')
    sg.component_on_face('f_lvg','cw3')
    
    
    #plinth
    sg.divide_mx('com',0.35,['flank','mid'])
    sg.divide_x('flank',[0.5,0.5],['A','B'])
    sg.scale_y('A',1.2,sg.Align.E)
    sg.scale_x('A',1.1,sg.Align.E)
    sg.divide_y('A',[0.3,0.4,0.3],['corner','ent'])
    sg.scale_z('corner',1.1,sg.Align.W)
    sg.decompose_4('corner')
    
    
    sg.scale_y('mid',1.2,sg.Align.W)
    sg.scale_z('mid',1.1,sg.Align.W)
    sg.divide_z('mid',[5,'r'],['m_l1','m_main'])
    sg.divide_z('B',[5,'r'],['f_l1','f_main'])
    sg.divide_z('ent',[5,'r'],['e_l1','e_main'])

    
    
    sg.ENGINE.add_step('{} ->T4-> {}'.format(name,out_names))


def main():
    reload(sg)
    sg.reset()
    rs.EnableRedraw(False)
    sg.create_box((200,300,1),name='start')
    SiteR1('start')
    rs.EnableRedraw(True)
    sg.end()
    
if __name__ == '__main__':
    main()




