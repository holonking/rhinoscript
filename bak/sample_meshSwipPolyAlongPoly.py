import Rhino
import rhinoscriptsyntax as rs

import rsTools
reload(rsTools)
from rsTools import *


profile=rs.GetObject('sel profile crv',4,False)
rail=rs.GetObject('sel rail crv',4,False)

meshSwipPolyAlongPoly(profile,rail)


#meshExtrudePolyToByVectPlane(poly,vect,pln)
