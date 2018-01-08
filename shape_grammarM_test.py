import rhinoscriptsyntax as rs
import RsTools.ShapeGrammarM as sg
reload(sg)

sg.reset()

#b=sg.create_box((56,20,80),name='start')
#b=sg.create_box((30,60,20),name='start')
sg.add_rhino_box('init','start')
sg.move('start',[0,10,0])
#sg.divide_x('start',[0.4,0.6],['A','B'])
sg.extract_face('start','S','face1')
sg.divide_face_uv('face1',1.5,3,'bay')
sg.import_component('component_cw_01','cw1')
sg.component_on_face('bay','cw1')
sg.end()


