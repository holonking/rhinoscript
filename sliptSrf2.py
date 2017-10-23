import rhinoscriptsyntax as rs

import rsTools
reload(rsTools)
from rsTools import *


trash=rs.ObjectsByLayer('Default')
rs.DeleteObjects(trash)
rs.CurrentLayer('Default')

iteration=0
objs=rs.ObjectsByLayer('GENMASSING')
srf=objs[0]




spliteIrregularPolygon(srf)
