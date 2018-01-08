import rhinoscriptsyntax as rs
#from RsTools import *
#reload(MeshTools)
import RsTools.ShapeGrammarM as sg
reload(sg)
from Rhino.Geometry import *

sg.reset()
sg.start()
sg.create_box([30,20,1],name='garden')
sg.divide_y('garden',[0.4,0.2,0.4],['g1','r','g2'])
sg.invert_x('g2')
sg.rename('g1','g')
sg.rename('g2','g')
sg.divide_x('g',[0.3,0.1,0.6],['g1','r','g2'])
sg.invert_x('g2')

for i in range(2):
    sg.rename('g1','g')
    sg.rename('g2','g')
    sg.divide_x('g',[0.3,0.7],['g1','g2'])
    sg.invert_y('g2')

    
    sg.rename('g1','g')
    sg.rename('g2','g')
    sg.divide_y('g',[0.3,0.7],['g1','g2'])
    sg.invert_x('g2')

    
        

sg.scale_z('g1',1.2)


sg.end()