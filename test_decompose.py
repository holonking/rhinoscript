import rhinoscriptsyntax as rs
#from RsTools import *
#reload(MeshTools)
import RsTools.ShapeGrammarM as sg
reload(sg)
from Rhino.Geometry import *
sg.reset()
sg.start()

sg.create_box([30,20,60],name='init')
sg.decompose_4('init')


sg.end()