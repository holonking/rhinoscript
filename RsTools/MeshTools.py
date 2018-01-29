import linecache
import sys
import Rhino
import rhinoscriptsyntax as rs
from Rhino.Geometry import Point3d, Vector3d, Plane, Mesh


TOLERANCE = 0.0001
class BOX_FACE_ID:
    front=0
    back=1
    left=2
    right=3
    bottom=4
    top=5

def create_mesh_box(position=Point3d(0,0,0),
                    vects=(Vector3d(1,0,0),Vector3d(0,1,0),Vector3d(0,0,1)),
                    size=Vector3d(0,0,0),normals=None):
    org = position
    x = vects[0]
    y = vects[1]
    z = vects[2]
    ax = size[0] * x
    ay = size[1] * y
    az = size[2] * z

    #3--2 7--6
    #| b| | t|
    #0--1 4--5
    #org

    pts=[0]*8
    faces=[]
    pts[0] = Point3d(org)
    pts[1] = org + ax
    pts[2] = pts[1] +ay
    pts[3] = org + ay
    for i in range(4,8):
        pts[i]=pts[i-4]+az
    #front and back

    meshpts=[]
    #front back
    meshpts+=[Point3d(pts[0]),Point3d(pts[1]),Point3d(pts[5]),Point3d(pts[4])]
    meshpts+=[Point3d(pts[2]), Point3d(pts[3]), Point3d(pts[7]), Point3d(pts[6])]
    #left right
    meshpts += [Point3d(pts[3]), Point3d(pts[0]), Point3d(pts[4]), Point3d(pts[7])]
    meshpts += [Point3d(pts[5]), Point3d(pts[1]), Point3d(pts[2]), Point3d(pts[6])]
    #top bot
    meshpts += [Point3d(pts[0]), Point3d(pts[3]), Point3d(pts[2]), Point3d(pts[1])]
    meshpts += [Point3d(pts[4]), Point3d(pts[5]), Point3d(pts[6]), Point3d(pts[7])]

    j=0
    for i in range(6):
        faces.append((j,j+1,j+2,j+3))
        j+=4

    mesh_id = rs.AddMesh(meshpts,faces,normals)
    return mesh_id

def get_face_info(meshface):
    total_width = meshface.Vertices[1].DistanceTo(meshface.Vertices[0])
    total_height = meshface.Vertices[2].DistanceTo(meshface.Vertices[1])
    vect_u = rs.VectorUnitize( meshface.Vertices[1] - meshface.Vertices[0] )
    vect_v = rs.VectorUnitize( meshface.Vertices[2] - meshface.Vertices[1] )
    return total_width,total_height,vect_u,vect_v

def scale_face(meshface,scale=[1,1], ratio_mode=True, offset=None):
    W,H,U,V=get_face_info(meshface)
    if ratio_mode:
        size_u=scale[0]*W
        size_v=scale[1]*H
    else:
        size_u=scale[0]
        size_v=scale[1]
    size=[size_u,size_v]

    u=U
    v=V
    #u=rs.VectorUnitize(U)
    #v=rs.VectorUnitize(V)

    pts=[]
    pts.append(Point3d(meshface.Vertices[0]))
    pts.append(pts[0] + (u * size[0]))
    pts.append(pts[1] + (v * size[1]))
    pts.append(pts[0] + (v * size[1]))

    if offset:
        for i in range(len(pts)):
            pts[i]=pts[i]+offset

    face=addMeshQuad(pts)
    return face

def box_face(mesh, index=BOX_FACE_ID.front, add_doc=True):
    try:
        mesh=rs.coercemesh(mesh)
    except:
        pass
    if not isinstance(mesh, Rhino.Geometry.Mesh):
        print('given mesh is not Mesh, mesh={}'.format(type(mesh)))
        return

    mesh_face=mesh.Faces[index]
    verts=[]
    for i in mesh_face:
        verts.append(Point3d(mesh.Vertices[i]))
    return addMeshQuad(verts)


def addMeshQuad(verts):
    faces = [(0, 1, 2, 3)]
    mesh = rs.AddMesh(verts, faces)
    return mesh

def meshExtrudePolyByVect(poly, vect, colorRow=None):

    pts = rs.CurveEditPoints(poly)
    meshExtrudePtsByVect(pts, vect, colorRow)

def meshExtrudePtsByVect(pts, vect, colorRow=None, add_doc=False):
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