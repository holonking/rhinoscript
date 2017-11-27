import rhinoscriptsyntax as rs
import Rhino.Geometry as rg
import Rhino
from Rhino.Geometry import *

class BoxTransformer:
    def __init__(self, box=None):
        self.box=box
    def transform(self):
        #override this method
        pass

class BT_classic_1(BoxTransformer):
    def __init__(self,box=None):
        super(BT_classic_1,self).__init__()
    def transform(self):
        if len(rg.Brep.Faces) == 6:
            Rhino.RhinoApp.WriteLine('is box')

def is_solid_box(brepid):
    # stricktly checks if the brep is a solid box
    # returns bool,org_vect
    # org_vect is a list of
    # [Point3d:org, Vector3d u, Vector3d v, Vector3d h]
    # vectors are not unitized
    brep = rs.coercebrep(brepid)

    if not brep.IsSolid:
        return False,None
    counter = 0
    edges = []
    edge_pts=[]
    for f in brep.Faces:
        counter += 1
        if counter > 6:
            return False
        flag, plane = f.TryGetPlane()
        if flag:
            if plane.ZAxis[2] == 1 or plane.ZAxis[2] == -1:
                pts=[]
                egs=rg.PolyCurve()
                for e in f.AdjacentEdges():
                    p=brep.Edges[e].PointAtStart
                    pts.append(p)
                    egs.Append(brep.Edges[e])
                edges.append(egs)
                edge_pts.append(pts)

        else:
            return False

    if counter == 6:
        print(edge_pts[0][0],edge_pts[1][0])
        if edge_pts[0][0].Z>edge_pts[1][0].Z:
            arrx= edges[0].ClosestPoint(edge_pts[1][0])
            cp = edges[0].PointAt(arrx[1])
            w = cp-edge_pts[1][0]
            org = edge_pts[1][0]
        else:
            arrx= edges[1].ClosestPoint(edge_pts[0][0])
            cp=edges[1].PointAt(arrx[1])
            w = cp - edge_pts[0][0]
            org = edge_pts[0][0]
        u=edge_pts[0][1]-edge_pts[0][0]
        v=edge_pts[0][2]-edge_pts[0][1]

        if u.Length>v.Length:
            t=v
            v=u
            u=t
        return True,(org,u,v,w)
    return False,None


def box_div_h(brepids,ratio=[0.5,0.5],names=None,delete_input=False):
    if isinstance(brepids,dict):
        brepids=brepids.values()
    elif not isinstance(brepids,list):
        brepids=[brepids]
    comps = []
    for brepid in brepids:
        flag,org_vects=is_solid_box(brepid)
        vect=Vector3d(0,0,0)
        if flag:
            for i in range(len(ratio)):
                r=ratio[i]
                if r==0:
                    continue
                comp=genbox_from_org_vects(org_vects,(1,r,1))
                if i>0:
                    vect=vect+org_vects[2]*ratio[i-1]
                    rs.MoveObject(comp,vect)
                comps.append(comp)
    if delete_input:
        rs.DeleteObjects(brepids)
    if len(comps)>0:
        return comps
    return None

def box_div_v(brepids,ratio=[0.6,0.4],names=None,delete_input=False):
    if isinstance(brepids, dict):
        brepids = brepids.values()
    elif not isinstance(brepids,list):
        brepids=[brepids]
    comps = []
    for brepid in brepids:
        flag, org_vects = is_solid_box(brepid)
        vect = Vector3d(0, 0, 0)
        if flag:
            for i in range(len(ratio)):
                r = ratio[i]
                if r==0:
                    continue
                comp = genbox_from_org_vects(org_vects, (1, 1, r))
                if i > 0:
                    vect = vect+org_vects[3] * ratio[i - 1]
                    rs.MoveObject(comp, vect)
                comps.append(comp)
    if delete_input:
        rs.DeleteObjects(brepids)
    if len(comps) > 0:
        return comps
    return None

def genbox_from_org_vects(org_vects,scale=(1,1,1)):
    org=org_vects[0]
    u=org_vects[1]*scale[0]
    v=org_vects[2]*scale[1]
    w=org_vects[3]*scale[2]

    pts=[]
    pts.append(org)
    pts.append(org + u)
    pts.append(org + u + v)
    pts.append(org + v)
    pts.append(org)

    poly=rs.AddPolyline(pts)
    box=rs.ExtrudeCurveStraight(poly,org,org+w)
    rs.CapPlanarHoles(box)
    rs.DeleteObjects([poly])
    return box



