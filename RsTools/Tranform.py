import linecache
import sys
import Rhino
import rhinoscriptsyntax as rs
from RsTools.Types import *
import RsTools.Analysis as rta


TOLERANCE = 0.001



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




def component_match_mesh(component, mesh):
    def get_quade_orientations(component, quade):
        bb = rs.BoundingBox(component)

        ox = rs.VectorLength(bb[1] - bb[0])
        oy = rs.VectorLength(bb[2] - bb[1])
        oz = rs.VectorLength(bb[4] - bb[0])
        return (ox, oy, oz)

    ocomps = []
    op1 = []
    ov = []
    for f in mesh.Faces:
        v1 = mesh.Vertices[f[0]]
        v2 = mesh.Vertices[f[1]]
        v3 = mesh.Vertices[f[2]]
        v4 = mesh.Vertices[f[3]]
        tx = rs.VectorLength(v2 - v1)
        tz = rs.VectorLength(v3 - v2)
        op1.append(v1)
        ov.append(v2 - v1)
        # print(tx,ty)
        ox, oy, oz = get_quade_orientations(component, mesh)
        scalex = tx / ox
        scalez = tz / oz
        cv1 = Vector3d(1, 0, 0)
        cv2 = rs.VectorUnitize(v2 - v1)
        angle = rs.VectorAngle(cv1, cv2)

        # print angle,dot
        radians = math.radians(angle)
        if rs.VectorCrossProduct(cv2, cv1).Z > 0:
            radians *= -1
        c = math.cos(radians)
        s = math.sin(radians)

        matrixS = [[scalex, 0, 0, 0],
                   [0, 1, 0, 0],
                   [0, 0, scalez, 0],
                   [0, 0, 0, 1]
                   ]
        matrixR = [[c, -s, 0, v1.X],
                   [s, c, 0, v1.Y],
                   [0, 0, 1, v1.Z],
                   [0, 0, 0, 1]
                   ]

        o = rs.TransformObject(component, matrixS, True)
        o = rs.TransformObject(o, matrixR, False)
        ocomps.append(o)
    return ocomps
