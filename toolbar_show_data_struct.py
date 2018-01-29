
import rhinoscriptsyntax as rs
from RsTools import ShapeGrammarM as sg
from RsTools.Colors import ColorWheel 
import clr
clr.AddReference('IronPython.Wpf')
import wpf
import System
import System.Windows.Controls as ws


try:
    eg=sg.ENGINE
    for o in eg.data:
        if o._parent is None:
            o.print_tree()
        #else: print('* {}.{}'.format(o._parent,o))
    
except Exception as e:
    print(e)
    pass
    