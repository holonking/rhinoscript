import System
import System.Windows.Forms as Forms
from System.Windows.Forms import *
import System.Drawing as Drawing
from System.Drawing import *
import Rhino
import rhinoscriptsyntax as rs



baseObj=rs.AddLine((0,0,0),(0,-200,0))
poly=rs.GetObject('sel crv',4,False)

pts=rs.CurveEditPoints(poly)
rs.AddPoints(pts)

def orientObjAlongPolyPts(obj,pts,baseVect=(0,1,0)):
    up=(0,0,1)
    for i in range(0,len(pts)-1):
        if i<(len(pts)-2):
            p0=pts[i]
            p1=pts[i+1]
            p2=pts[i+2]

            v1=rs.VectorUnitize(p1-p0)
            v2=rs.VectorUnitize(p2-p1)
            n1=rs.VectorCrossProduct(v1,up)
            n2=rs.VectorCrossProduct(v2,up)
            mid=rs.VectorAdd(n1,n2)
            n=rs.VectorUnitize(mid)
        else:
            p0=pts[i]
            p1=pts[i+1]
            v1=rs.VectorUnitize(p1-p0)
            n=rs.VectorCrossProduct(v1,up)

        rs.AddLine(p1,p1+n)

        a=rs.VectorAngle((0,1,0),n)
        rs.OrientObject(obj,[(0,0,0),baseVect],[p1,p1+n],1)

orientObjAlongPolyPts(baseObj,pts)
