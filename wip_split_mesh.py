import rhinoscriptsyntax as rs
from Rhino.Geometry import *
import Rhino




def point_on_plane_top(pt,plane, reverse=False): 
    testVect=plane.XAxis
    if plane.XAxis.Z !=0:
        testVect=plane.YAxis
    
    pp1=plane.Origin
    pp2=pp1 +testVect
    
    v1=pp1-pt
    v2=pp2-pt
    n=rs.VectorCrossProduct(v1,v2)
    flag = n.Z > 0
    if reverse:
        return not flag
    return flag

def get_split_point(p1,p2,plane):
    line=LineCurve(p1,p2)
    arrx=Rhino.Geometry.Intersect.Intersection.CurvePlane(line,plane,0.001)
    if arrx:
        return arrx[0].PointA
    return None

def mesh_plane_trim(m,plane,reverse=False):
    fms=[]
    for f in m.Faces:
        fm=mesh_face_plane_trim(m,f,plane,reverse)
        if fm:
            fms.append(fm)
            
    if len(fms) > 0:
        nm=Mesh()
        for fm in fms:
            nm.Append(fm)
        pls=Rhino.Geometry.Intersect.Intersection.MeshPlane(m,plane)
        if pls and len(pls[0])>3:
            print('poly length=',len(pls[0]))
            if len(pls[0])<=5:
                pts=list(pls[0])[:-1]
                sm=Mesh()
                for p in pts:
                    sm.Vertices.Add(p)
                sm.Faces.AddFace(*range(len(pts)))
            else :
                sm=Rhino.Geometry.Mesh.CreateFromClosedPolyline(pls[0])
            nm.Append(sm)
        return nm
        
    return None

def mesh_face_plane_trim(m,f,plane,reverse=False):
    pts=[]
    left=[]
    right=[]
    
    for i in f:
        p=m.Vertices[i]
        #rs.AddTextDot(i,p)
        pts.append(Point3d(p))
    pts.append(pts[0])
    last_side='on'
    for i in range(len(pts)):
        p=pts[i]
        if point_on_plane_top(p,plane,reverse):
            if last_side == 'right':
                np = get_split_point(p,pts[i-1],plane)
                if np:
                    left.append(np)
            left.append(p)
            last_side = 'left'
        else:
            if last_side == 'left':
                np = get_split_point(p,pts[i-1],plane)
                if np:
                    left.append(np)
            last_side='right'
    if len(left) < 1:
        return None
    if left[-1].DistanceTo(left[0])<0.01:
        left=left[:-1]
    #rs.AddPoints(left)
    #print(len(left))
    
    if len(left) <= 4:
        fm=Mesh()
        for p in left:
            fm.Vertices.Add(p)
        fm.Faces.AddFace(*range(len(left)))
        return fm
    else:
        left.append(left[0])
        poly=Polyline(left)
        fm=Rhino.Geometry.Mesh.CreateFromClosedPolyline(poly)
        return fm
    return None

#f=m.Faces[0]
#split_mesh_face(f,plane)

k=rs.GetObject('sel')
m=rs.coercemesh(k)
plane=rs.WorldZXPlane()


m=mesh_plane_trim(m,plane,reverse=True)
Rhino.RhinoDoc.ActiveDoc.Objects.AddMesh(m)
Rhino.RhinoDoc.ActiveDoc.Views.Redraw()

#
#ngons=m.Ngons
#tvs=m.TopologyVertices
#for i in range(len(tvs)):
#    rs.AddTextDot(i,tvs[i])
#    print(i)
