import Rhino
import rhinoscriptsyntax as rs

#for WIP modules, must import and reload
#to keep loading the most updated module
#and then from module import *
import rsTools
reload(rsTools)
from rsTools import *

path='~/Documents/Design/component.3dm'
component=importComponent(path)
print('what have we got?')
