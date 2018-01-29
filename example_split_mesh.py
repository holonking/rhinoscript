import Rhino
from Rhino.Geometry import Point3d, Vector3d
import Rhino.Geometry as rg
import rhinoscriptsyntax as rs

def point_on_plane_top(pt,plane): 
    testVect=plane.XAxis
    if plane.XAxis.Z !=0:
        testVect=plane.YAxis
    
    pp1=plane.Origin
    pp2=pp1 +testVect
    
    v1=pp1-pt
    v2=pp2-pt
    n=rs.VectorCrossProduct(v1,v2)
    return n.Z > 0



guid=rs.GetObject('sel')
mesh=rs.coercemesh(guid)
print(mesh)

plane=rs.WorldZXPlane()
print(plane)
print(plane.ZAxis)

#intersect
pls=Rhino.Geometry.Intersect.Intersection.MeshPlane(mesh,plane)
for pl in pls:
    for i in range(len(pl)):
        p=pl[i]
        rs.AddTextDot(i,p)
    rs.AddPolyline(pl)
    

Rhino.Geometry.Mesh.Faces
left=[]
right=[]
counter=0
for mf in mesh.Faces:
    indice=[mf.A,mf.B,mf.C,mf.D]
    pts=[]
    ttp=Point3d(0,0,0)
    for i in indice:
        p=mesh.Vertices[i]
        pts.append(p)
        #rs.AddPoint(p)
        ttp += Point3d(p.X,p.Y,p.Z)
    center=ttp/4
    rs.AddTextDot(counter,center)
    counter+=1


# 1 首先实现point on left/right
# 2 判断是否quad
# 3 quad 情况 3中
