import Rhino
import rhinoscriptsyntax as rs
import rsTools
reload(rsTools)
from rsTools import *


srf=rs.GetObject('sel srf',16)

divSrfVects(srf)

#poly=divEQCrvToPolyAD(crv,w=900,adjacentCrvs=adj)
