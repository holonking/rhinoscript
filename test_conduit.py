from ShapeGrammar.conduit.displayEngine import DisplayEngine
from ShapeGrammar.conduit.monitor import ConduitMonitor
from ShapeGrammar.core.geometries import Pivot, Scope
from Rhino.Geometry import *


s1=Scope(Pivot())
print('----',str(s1.pivot))
s1.set_size(Vector3d(1,1.3,2))
s1.rotate(0)

s2=Scope()
s2.move(Vector3d(1.5,0.6,0.2))
s2.rotate(15)
s2.flip(0)

s1.turn(3)


engine=DisplayEngine()
engine.add(s1,'fore')
engine.add(s2,'fore')
cm=ConduitMonitor(engine)

