import Rhino
from Rhino.Geometry import *
import RsTools.MeshTools as rt
reload(rt)
import rhinoscriptsyntax as rs

box=rt.create_mesh_box(size=Vector3d(60,20,80))
face=rt.box_face(box,rt.BOX_FACE_ID.front)
rs.SelectObject(face)

