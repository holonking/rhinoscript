import linecache
import sys
import Rhino
import rhinoscriptsyntax as rs
TOLERANCE = 0.0001
import RsTools.Analysis as rta
import RsTools.Divide as rtd
import RsTools.Mesh as rtm
from RsTools.Types import *


def mesh_extrude_crv_to_Pattern(crv, facadeType, totalHeightVect):
    crv = rs.CopyObject(crv)
    global TYPECOLORS
    totalLength = rs.VectorLength(totalHeightVect)
    restLength = totalLength
    length = facadeType.heights[0]
    counter = 0
    meshes = []

    def genRow(crv, length, facadeType, counter):
        patterIndex = counter % len(facadeType.pattern)
        extrudeVect = Rhino.Geometry.Vector3d(0, 0, length)
        pts = rtd.div_crv_by_lengths(crv, facadeType.widths)
        colorRow = rtm.genMeshColorRow(pts, facadeType.pattern[patterIndex], TYPECOLORS)
        m = rtm.meshExtrudePtsByVect(pts, extrudeVect, colorRow)
        return m

    if length > 0:
        while restLength - length > 0:
            m = genRow(crv, length, facadeType, counter)
            meshes.append(m)
            # prepare for next round
            counter += 1
            restLength -= length
            if counter > 20: break
            crv = rs.MoveObject(crv, Rhino.Geometry.Vector3d(0, 0, length))
            length = facadeType.heights[counter % len(facadeType.heights)]
            # print('length:',length)
            # print('rest length:',restLength)
            if length == -1: break

    if restLength > 0:
        finalLength = restLength
        # print('final length:',finalLength)
        m = genRow(crv, finalLength, facadeType, counter)
        meshes.append(m)
    rs.DeleteObject(crv)
    return rs.JoinMeshes(meshes, True)

def divide_drf_to_pattern(srf, facadeType):
    top, bot, verts = rta.getSrfTopBotVertCrvs(srf)

    if bot is None:
        # print('bot is None exit')
        return None
    if not rs.IsCurve(bot):
        # print('bot is not Curve exit')
        return None
    if len(verts) < 1:
        # print('len(verts)<1')
        return None
    if not rs.IsCurve(verts[0]):
        # print('verts[0] is not a curve')
        return None

    p0 = rs.CurveStartPoint(verts[0])
    p1 = rs.CurveEndPoint(verts[0])
    if p1[2] > p0[2]:
        vect = p1 - p0
    else:
        vect = p0 - p1
    # print(vect)

    m = mesh_extrude_crv_to_Pattern(bot, facadeType, vect)
    rs.DeleteObjects([top, bot])
    rs.DeleteObjects(verts)

    return m

def importComponent(path):
    if path is None: return None
    imported = rs.Command("-Insert " + path + ' Objects Enter 0,0,0 1 0')
    outComponent = AttrDict()

    if imported:
        components = rs.LastCreatedObjects()
        outComponent.polys = []
        outComponent.breps = []
        for comp in components:
            if rs.IsCurve(comp): outComponent.polys.append(comp)
            if rs.IsBrep(comp): outComponent.breps.append(comp)
        return outComponent


def applyComponent(filePath, polyAD):
    trash = []
    out = []

    # load the component
    component = None
    try:
        component = importComponent(filePath)
    except:
        print('exception on importing module')

    if component is None:
        # print('component is None, check import path')
        return None

    pts = polyAD.points
    nmls = polyAD.normals
    dirs = polyAD.directions

    # initial orientation for the component
    orientation = pts[1] - pts[0]
    for c in component.polys:
        trash.append(c)
        # mesh=meshSwipPolyAlongPoly(c,pts,numls)
