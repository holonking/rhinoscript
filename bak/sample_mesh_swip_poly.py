import System
import System.Windows.Forms as Forms
from System.Windows.Forms import *
import System.Drawing as Drawing
from System.Drawing import *
import Rhino
import rhinoscriptsyntax as rs
import os
from os import path

import rsUI
reload(rsUI)
from rsUI import *

import rsTools
reload(rsTools)
from rsTools import *

rail=rs.GetObject('sel rail',4)
profile=rs.GetObject('sel profile',4)
p1=rs.CurveStartPoint(rail)
p2=rs.CurveEndPoint(rail)
vect=p2-p1

meshExtrudePolyByVect(profile,vect)
#meshSwipPolyAlongPoly(profile,rail)
