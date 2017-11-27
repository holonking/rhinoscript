import linecache
import sys
import Rhino
import rhinoscriptsyntax as rs

TOLERANCE = 0.0001

def addMeshQuad(verts):
    faces = [(0, 1, 2, 3)]
    mesh = rs.AddMesh(verts, faces)
    return mesh


def meshExtrudePolyByVect(poly, vect, colorRow=None):
    pts = rs.CurveEditPoints(poly)
    meshExtrudePtsByVect(pts, vect, colorRow)


def meshExtrudePtsByVect(pts, vect, colorRow=None):
    extrudeVect = vect
    # rs.AddPoints(pts)
    meshes = []
    # verts=[]
    # faces=[]
    for i in range(0, len(pts) - 1):
        p1 = pts[i]
        p2 = pts[i + 1]
        p1up = p1 + extrudeVect
        p2up = p2 + extrudeVect
        m = addMeshQuad([p1, p1up, p2up, p2])
        if colorRow is not None:
            # rs.ObjectColor(m,colorRow[i])
            rs.MeshVertexColors(m, [colorRow[i], colorRow[i], colorRow[i], colorRow[i]])
        meshes.append(m)
    mesh = rs.JoinMeshes(meshes, True)
    return mesh


def meshExtrudePolyToByVectPlane(poly, vect, pln):
    extrudeVect = vect

    # find far line from vector to be intersected later
    farvect = rs.VectorScale(extrudeVect, 1000)
    pts = rs.CurveEditPoints(poly)

    meshes = []
    for i in range(0, len(pts) - 1):
        p1 = pts[i]
        p2 = pts[i + 1]

        line = [p1, p1 + farvect]
        p1pj = rs.LinePlaneIntersection(line, pln)
        line = [p2, p2 + farvect]
        p2pj = rs.LinePlaneIntersection(line, pln)
        m = addMeshQuad([p1, p1pj, p2pj, p2])
        meshes.append(m)

    pjPolyPts = []
    for p in pts:
        line = [p, p + farvect]
        xp = rs.LinePlaneIntersection(line, pln)
        pjPolyPts.append(xp)

    mesh = rs.JoinMeshes(meshes, True)
    return mesh, pjPolyPts


def meshSwipPolyAlongPolyAD(profile, polyAD):
    profile = rs.CopyObject(profile)
    pts = polyAD.points
    # TODO: finish the following function
    # the swip has to project the profile to start and end plane
    # not finished


def meshSwipPolyAlongPoly(profile, rail):
    profile = rs.CopyObject(profile)
    pts = rs.CurveEditPoints(rail)
    baseVect = Rhino.Geometry.Point3d(0, 1, 0)

    meshes = []
    for i in range(0, len(pts) - 2):
        p0 = pts[i]
        p1 = pts[i + 1]
        p2 = pts[i + 2]

        v1 = rs.VectorUnitize(p1 - p0)
        v2 = rs.VectorUnitize(p2 - p1)
        rv1 = rs.VectorUnitize(p0 - p1)
        vect = p1 - p0

        mid = rs.VectorUnitize((rv1 + v2) / 2)
        np = p1 + mid
        up = p1 + Rhino.Geometry.Point3d(0, 0, 1)
        pln = rs.PlaneFromPoints(p1, np, up)

        mesh, pjpts = meshExtrudePolyToByVectPlane(profile, vect, pln)
        meshes.append(mesh)
        rs.DeleteObject(profile)
        profile = rs.AddPolyline(pjpts)

    mesh = rs.JoinMeshes(meshes, True)
    rs.DeleteObject(profile)
    return mesh

def genMeshColorRow(pts, pattern, colors):
    colorRow = []
    for i in range(0, len(pts)):
        pi = i % len(pattern)
        index = pattern[pi]
        c = colors[index]
        colorRow.append(c)
    return colorRow