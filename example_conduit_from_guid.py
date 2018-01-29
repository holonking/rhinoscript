from ShapeGrammar.conduit.displayEngine import DisplayEngine
from ShapeGrammar.conduit.monitor import ConduitMonitor
from ShapeGrammar.core.geometries import Pivot, Scope
from Rhino.Geometry import *
import rhinoscriptsyntax as rs
import Rhino

from ShapeGrammar.conduit.monitor import ConduitMonitor
from ShapeGrammar.conduit.displayEngine import DisplayEngine

#select a brep
guid=rs.GetObject('sel')
t=rs.ObjectType(guid)

#tr=Rhino.Geometry.Transform.Rotation(45,Point3d(3,3,0))
#rs.TransformObject(guid,tr,True)

brep=rs.coercebrep(guid)
maxLength=0
maxs=None
maxe=None
for e in brep.Edges:
    length=e.GetLength()
    if length>maxLength:
        maxLength=length
        maxs=e.PointAtStart
        maxe=e.PointAtEnd

rs.AddPoints([maxs,maxe])
vx=maxe-maxs
vy=Vector3d.CrossProduct(vx,Vector3d(0,0,1))
vy*=-1
pln=Plane(maxs,vx,vy)
bbox=rs.BoundingBox(guid,pln)

s=Scope.create_from_bbox(bbox)
s.turn(2)
engine=DisplayEngine()
engine.add(s)
cm=ConduitMonitor(engine)

