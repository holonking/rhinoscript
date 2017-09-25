import Rhino
import rhinoscriptsyntax as rs
import math
import rsTools
reload(rsTools)
from rsTools import *

srfs=rs.ObjectsByLayer('selSrf')

#sort by types
colors=[(200,200,255),
        (180,220,255),
        (160,240,255),
        (140,260,255)]
t1=[]
t2=[]
t3=[]
types=[t1,t2,t3]

#clear and set active genType layer
rs.CurrentLayer('genType')
trash=rs.ObjectsByLayer('genType')
for t in trash:
    if rs.IsObject(t):rs.DeleteObject(t)

#sort srfs by types ->types[i]->[]
for f in srfs:
    name=rs.ObjectName(f)
    for i in range(0,3):
        txt=str(i+1)
        if name==txt:
            print('txt: ',txt)
            print('name :',name)
            nf=rs.CopyObject(f)
            rs.ObjectLayer(nf,'genType')
            rs.ObjectColor(nf,colors[i])
            types[i].append(nf)
            break

ct0p={'w':1500,'h':[600],'t'=[-1]}#stone
ct1p={'w':1500,'h':[4200,-1],'t'=[-1,0]}#doors
ct2p={'w':1500,'h':[6000],'t'=[-1]}#double height glass
compTypes=[ct0p,ct1p,ct2p]

for i in range(0,len(types)):
    srfs=types[i]
    for f in srfs:
        ctp=compTypes[i]
        w==ctp['w']
        h=ctp['h']
        t=ctp['t']

        if ctp[-1]==-1: hctp=sum(ctp[:-1])
        else:hctp=sum(ctp)

        top,bot,verts=getSrfTopBotVertCrvs(s)
        p1=rs.CurveStartPoint(verts[0])
        p2=rs.CurveEndPoint(verts[0])
        if p1[2]>p2[2]: extrudeVect=p1-p2
        else: extrudeVect=p2-p1
        srfH=rs.VectorLength(extrudeVect)
        uextrudeVect=rs.VectorUnitize(extrudeVect)
        count=srfH/hctp
        if count<0:
            count=1
            ctp=[srfH-hctp]
        else:
            count=math.ceil(count)
            



# rs.CurrentLayer('genMesh')
def divSrfsToMesh(srfs,width=1500,extrudeVect=None):
    meshes=[]
    for s in srfs:
        if not rs.IsSurface(s):continue
        top,bot,verts=getSrfTopBotVertCrvs(s)

        if extrudeVect is None:
            p1=rs.CurveStartPoint(verts[0])
            p2=rs.CurveEndPoint(verts[0])
            if p1[2]>p2[2]: extrudeVect=p1-p2
            else: extrudeVect=p2-p1
        if bot is None:
            continue

        pts=rs.DivideCurve(bot,round(rs.CurveLength(bot)/width))
        meshes.append(meshExtrudePtsByVect(pts,extrudeVect))

        rs.DeleteObjects([top,bot])
        rs.DeleteObjects(verts)


    mesh=rs.JoinMeshes(meshes,True)
    return mesh

def getMeshSharedNormals(mesh):
    omesh=rs.MeshOffset(mesh,1)
    pts=rs.MeshVertices(mesh)
    ptso=rs.MeshVertices(omesh)
    vects=[]
    for p0,p1 in zip(pts,ptso):
        v=p1-p0
        vects.append(v)

    rs.DeleteObject(omesh)
    return vects



# mesh=divSrfsToMesh(srfs)
#vects=getMeshSharedNormals(mesh)
#drawVectors(rs.MeshVertices(mesh),vects)

rs.LayerVisible('selSrf',False)
