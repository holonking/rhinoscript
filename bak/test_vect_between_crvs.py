import Rhino
from Rhino.Geometry import Point3d,Vector3d
import rhinoscriptsyntax as rs
import rsTools
reload(rsTools)
from rsTools import *



def testFunc():
    sel=rs.ObjectsByLayer('Default')
    crv=sel[0]
    compare=sel[1]
    index,normal=findSharedbisecNormal(crv,compare)
    print(index)
    if index==0:
        p=rs.CurveStartPoint(crv)
        rs.AddLine(p,p+normal)
    elif index==1:
        p=rs.CurveEndPoint(crv)
        rs.AddLine(p,p+normal)


testFunc()
