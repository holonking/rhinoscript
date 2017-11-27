import linecache
import sys
import Rhino
import rhinoscriptsyntax as rs
from RsTools.Types import *
import RsTools.Analysis as rta

def orientObjAlongPolyPts(obj, pts, basePoint=(0, 0, 0), baseVect=(0, 1, 0)):
    # print('orient obj along poly points')
    up = (0, 0, 1)
    generatedObjects = []
    for i in range(0, len(pts) - 1):

        if i < (len(pts) - 2):
            p0 = pts[i]
            p1 = pts[i + 1]
            p2 = pts[i + 2]

            v1 = rs.VectorUnitize(p1 - p0)
            v2 = rs.VectorUnitize(p2 - p1)
            n1 = rs.VectorCrossProduct(v1, up)
            n2 = rs.VectorCrossProduct(v2, up)
            mid = rs.VectorAdd(n1, n2)
            n = rs.VectorUnitize(mid)
        else:
            p0 = pts[i]
            p1 = pts[i + 1]
            v1 = rs.VectorUnitize(p1 - p0)
            n = rs.VectorCrossProduct(v1, up)

        rs.AddLine(p1, p1 + n)

        a = rs.VectorAngle((0, 1, 0), n)
        gen = rs.OrientObject(obj, [basePoint, basePoint + baseVect], [p1, p1 + n], 1)
        generatedObjects.append(gen)
        # g=rs.AddGroup()
        # groupObjects=rs.AddObjectsToGroup(generatedObjects,g)
        return generatedObjects

