import linecache
import sys
import Rhino
import rhinoscriptsyntax as rs
from RsTools.Types import *
import RsTools.Analysis as rta


TOLERANCE = 0.001

def divide_surface(srf, width, height, return_type='points'):
    # return type can be 'mesh' or 'points'

    dom_u = srf.Domain(0)
    dom_v = srf.Domain(1)

    print(dom_u)
    print(dom_v)

    # find the horizontal isocurve
    crv = srf.IsoCurve(0, dom_u[0])
    pe = crv.PointAtEnd
    ps = crv.PointAtStart
    if abs(ps[2] - pe[2]) < TOLERANCE:
        iso_hr = crv
        iso_vr = srf.IsoCurve(1, dom_v[0])
        ihr = 0
        ivr = 1
    else:
        iso_hr = srf.IsoCurve(1, dom_v[0])
        iso_vr = crv
        ihr = 1
        ivr = 0

    # divide the horizontal IsoCurve
    # and extract the vertical IsoCurves
    # ----------------------------------
    # calculate the number of division in the horizontal direction
    num_div_h = round(rs.CurveLength(iso_hr) / width)
    actual_width = rs.CurveLength(iso_hr) / num_div_h
    # ts=rs.DivideCurveEquidistant(crv,width,return_points=False)
    ts = iso_hr.DivideByCount(num_div_h, True)
    # ----------------------------------
    # vertial division
    verts = []
    iso_verts = []
    for t in ts:
        crv = srf.IsoCurve(ivr, t)
        iso_verts.append(crv)
        pts = rs.DivideCurveEquidistant(crv, height)
        verts.append(pts)
        print(t)

    ovects = []
    opts = []
    result = {}
    mesh_verts = []
    mesh_faces = []

    for i in range(len(verts) - 1):
        vert1 = verts[i]
        vert2 = verts[i + 1]
        for j in range(len(vert1) - 1):
            p1 = vert1[j]
            p2 = vert1[j + 1]
            p3 = vert2[j]
            p4 = vert2[j + 1]
            v1 = p2 - p1
            v2 = p3 - p1
            vn = rs.VectorUnitize(rs.VectorCrossProduct(v1, v2))
            opts.append(p1)
            ovects.append(vn)

            mesh_verts += [p1, p3, p4, p2]
            fi = len(mesh_verts) - 4
            mesh_faces.append((fi, fi + 1, fi + 2, fi + 3))

    mesh = rs.AddMesh(mesh_verts, mesh_faces)

    result['pts'] = opts
    result['vect'] = ovects
    result['iso_verts'] = iso_verts
    result['mesh'] = mesh

    return result
