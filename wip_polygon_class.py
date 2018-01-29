
from Rhino.Geometry import *
import rhinoscriptsyntax as rs
from ShapeGrammar.core.geometries import Pivot, Scope, Extrusion
from ShapeGrammar.conduit.monitor import ConduitMonitor
from ShapeGrammar.conduit.displayEngine import DisplayEngine

rs.WorldXYPlane()

g=rs.GetObject('se')

import ShapeGrammar
form=ShapeGrammar.core.geometries.ExtrBlock.create_from_brepid(g)
sp,far=form._split_dir_amp(0,12)
print(far)
form.visible_topo=False

#
#engine=DisplayEngine()
#engine.add(form)
#engine.add(sp)
#cm=ConduitMonitor(engine)




