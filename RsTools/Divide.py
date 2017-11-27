import linecache
import sys
import Rhino
import rhinoscriptsyntax as rs
from RsTools.Types import *
import Analysis as rta

TOLERANCE = 0.0001

def div_eq_crv_to_poly(crv, w=900, adjacentCrvs=None):
    outpoly = PolyAD()
    crvLen = rs.CurveLength(crv)
    numDiv = crvLen / w
    width = crvLen / round(numDiv)
    pts = rs.DivideCurve(crv, numDiv, False, True)
    # add to output
    outpoly.points = pts

    sharedNormals = [None, None]
    if adjacentCrvs is not None:
        sharedNormals = rta.get_shared_bisect_Normals(crv, adjacentCrvs)

    for i in range(0, len(pts) - 2):
        up = (0, 0, 1)

        #     direct   direct_end
        # (p0)-v1->(p1)-v2->(p2)
        #   |n_start |n      |n_end
        #   V        V       V

        p0 = pts[i]
        p1 = pts[i + 1]
        p2 = pts[i + 2]

        v1 = rs.VectorUnitize(p1 - p0)
        v2 = rs.VectorUnitize(p2 - p1)
        n1 = rs.VectorCrossProduct(v1, up)
        n2 = rs.VectorCrossProduct(v2, up)
        mid = rs.VectorAdd(n1, n2)
        n = rs.VectorUnitize(mid)

        direct = p1 - p0
        # add to output
        outpoly.directions.append(direct)

        if i == 0:
            if sharedNormals[0] is not None:
                n_start = sharedNormals[0]

            else:
                n_start = rs.VectorCrossProduct(v1, up)
            outpoly.normals.append(n_start)

        # add to output
        outpoly.normals.append(n)

        if i == len(pts) - 3:
            if sharedNormals[1] is not None:
                n_end = sharedNormals[1]
            else:
                n_end = rs.VectorCrossProduct(v2, up)
            outpoly.normals.append(n_end)
            direct_end = p2 - p1
            outpoly.directions.append(direct_end)

    return outpoly

def div_crv_by_lengths(crv, lengths):
    pc = rs.CurveStartPoint(crv)
    outPts = []
    outPts.append(pc)
    wi = 0

    xp = rta.get_xpts_curve_circles(crv, pc, lengths[wi])
    ##print('xp:',xp)
    count = 0
    while xp is not None:
        # count+=1
        # if count>15: break
        outPts.append(xp)
        pc = xp
        wi += 1
        if wi > len(lengths) - 1: wi = 0
        xp = rta.get_xpts_curve_circles(crv, pc, lengths[wi])
        ##print('length: ',lengths[wi])

    outPts.append(rs.CurveEndPoint(crv))
    return outPts

def divideCrv(crv, width):
    ds = rs.DivideCurve(crv, width, True)
    pts = []
    for d in ds:
        pts.append(rs.IsPointOnCurve(d))
    return pts