import rhinoscriptsyntax as rs

import rsTools
reload(rsTools)
from rsTools import *


def isVertical(crv,tolerance=0.0001):
    start=rs.CurveStartPoint(c)
    end=rs.CurveEndPoint(c)
    # if abs(start[2]-end[2])<tolerance: hor_crvs.append(c)
    if abs(start[1]-end[1])<tolerance and abs(start[0]-end[0])<tolerance:
        return True
    return False
def isHorizontal(crv,tolerance=0.0001):
    start=rs.CurveStartPoint(c)
    end=rs.CurveEndPoint(c)
    if abs(start[2]-end[2])<tolerance:
        return True
    return False


objs=rs.ObjectsByLayer('GENMASSING')
srf=objs[0]
print(srf)

boundary=rs.DuplicateSurfaceBorder(srf)
pts=rs.CurveEditPoints(boundary)
# rs.AddPoints(pts)
crvs=rs.ExplodeCurves(boundary,True)

hors=[]
for c in crvs:
    if isHorizontal(c): hors.append(c)

up=(0,0,100000000)
cutters=[]
for c in hors:
    p=rs.CurveStartPoint(c)
    start=rs.VectorSubtract(p,up)
    end=rs.VectorAdd(p,up)
    l=rs.AddLine(start,end)
    rs.ObjectName(l,'cutters')
    cutters.append(l)

rs.DeleteGroup('cutters')
group=rs.AddGroup('cutters')
rs.AddObjectsToGroup(cutters,'cutters')
# rs.Command('!_selname_pause_cutters')

guid=rs.Command('! -_SelGroup _cutters')
print(guid)



# rs.SplitBrep(srf,cutters)

# rs.SelectObjects(hors)
