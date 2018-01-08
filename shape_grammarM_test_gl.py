import rhinoscriptsyntax as rs
from Rhino.Geometry import *
import RsTools.ShapeGrammarM as sg
reload(sg)

from GrammarLib import *
import GrammarLib as gl




sg.reset()

sg.add_rhino_box('init')
gl.A_ScapeHouse('init','asd')

sg.end()