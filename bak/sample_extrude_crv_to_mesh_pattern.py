import Rhino
import rhinoscriptsyntax as rs
import cPickle as pkl
import rsTools
reload(rsTools)
from rsTools import *

#see sample_cpickle.py for serializations
#see gen_facade_types.py for the generation of facade library
facadeTypes=[]
import os
directory='./FacadePatterns/'
files=os.listdir(directory)
for f in files:
    if f.find('.facade')>0:
        filename=directory+f
        with open(filename,'rb') as fp:
            facadeTypes.append(pkl.load(fp))


TYPECOLORS=[(0,102,204),
            (51,153,255),
            (153,204,255),
            (255,204,204),
            (255,102,102),
            (153,0,0)]

#height of the srf
totalH=6
xcircles=[]
trash=[]

#crv intersect circle->xpts[]
def cxc(crv,pt,r,onlyNext=True):
    trash=[]
    xc=rs.AddCircle(pt,r)
    xx=rs.CurveCurveIntersection(crv,xc)
    xpts=[]
    if xx is None: return None
    #print('xx len:',len(xx))
    for xxe in xx:
        if xxe[0]==1:
            xpts.append(xxe[1])
    rs.DeleteObject(xc)
    dom=rs.CurveDomain(crv)
    # endT=rs.CurveClosestPoint(crv,rs.CurveEndPoint(crv))
    # print('endT :'endT)
    if onlyNext:
        centerT=rs.CurveClosestPoint(crv,pt)
        maxT=dom[0]
        maxI=0
        for i in range(0,len(xpts)):
            p=xpts[i]
            t=rs.CurveClosestPoint(crv,p)
            if t>maxT:
                maxT=t
                maxI=i
            # print(dom[1],centerT,t)
        if maxT>dom[1] or maxT<centerT:
            return None
        return xpts[maxI]
    return xpts
def divCrvByLengths(crv,lengths):
    pc=rs.CurveStartPoint(crv)
    outPts=[]
    outPts.append(pc)
    wi=0

    xp=cxc(crv,pc,lengths[wi])
    # print('xp:',xp)
    count=0
    while xp is not None:
        # count+=1
        # if count>15: break
        outPts.append(xp)
        pc=xp
        wi+=1
        if wi>len(lengths)-1:wi=0
        xp=cxc(crv,pc,lengths[wi])
        # print('length: ',lengths[wi])

    outPts.append(rs.CurveEndPoint(crv))
    return outPts
def genMeshColorRow(pts,pattern,colors):
    colorRow=[]
    for i in range(0,len(pts)):
        pi=i%len(pattern)
        index=pattern[pi]
        c=colors[index]
        colorRow.append(c)
    return colorRow

def meshExtrudeCrvToPattern(crv,facadeType,totalHeightVect):
    crv=rs.CopyObject(crv)
    global TYPECOLORS
    totalLength=rs.VectorLength(totalHeightVect)
    restLength=totalLength
    length=facadeType.heights[0]
    counter=0
    meshes=[]
    def genRow(crv,length,facadeType,counter):
        patterIndex=counter%len(facadeType.pattern)
        extrudeVect=Rhino.Geometry.Vector3d(0,0,length)
        pts=divCrvByLengths(crv,facadeType.widths)
        colorRow=genMeshColorRow(pts,facadeType.pattern[patterIndex],TYPECOLORS)
        m=meshExtrudePtsByVect(pts,extrudeVect,colorRow)
        return m

    if length>0:
        while restLength-length>0:
            m=genRow(crv,length,facadeType,counter)
            meshes.append(m)
            #prepare for next round
            counter+=1
            restLength-=length
            if counter>20:break
            crv=rs.MoveObject(crv,Rhino.Geometry.Vector3d(0,0,length))
            length=facadeType.heights[counter%len(facadeType.heights)]
            print('length:',length)
            print('rest length:',restLength)
            if length==-1:break

    if restLength>0:
        finalLength=restLength
        print('final length:',finalLength)
        m=genRow(crv,finalLength,facadeType,counter)
        meshes.append(m)
    rs.DeleteObject(crv)
    return rs.JoinMeshes(meshes,True)

def divideSrfToPattern(srf,facadeType):
    top,bot,verts=getSrfTopBotVertCrvs(srf)

    if bot is None:
        print('bot is None exit')
        return None
    if not rs.IsCurve(bot):
        print('bot is not Curve exit')
        return None
    if len(verts)<1:
        print('len(verts)<1')
        return None
    if not rs.IsCurve(verts[0]):
        print('verts[0] is not a curve')
        return None


    p0=rs.CurveStartPoint(verts[0])
    p1=rs.CurveEndPoint(verts[0])
    if p1[2]>p0[2]: vect=p1-p0
    else: vect=p0-p1
    m=meshExtrudeCrvToPattern(bot,facadeType,vect)
    rs.DeleteObjects([top,bot])
    rs.DeleteObjects(verts)
    return m

rs.CurrentLayer('genMesh')
#clear genMesh
trash=rs.ObjectsByLayer('genMesh')
if len(trash)>0: rs.DeleteObjects(trash)


srfs=rs.ObjectsByLayer('genType')
#srfs=rs.GetObjects('sel srf',16)
for s  in srfs:
    name=int(rs.ObjectName(s))
    typeI=name-1
    facadeType=facadeTypes[typeI]
    divideSrfToPattern(s,facadeType)

vect=Rhino.Geometry.Point3d(0,0,13000)
# pts=divCrvByLengths(crv,widths)
# colorRow=genMeshColorRow(pts,pattern[0],typeColors)
# meshExtrudePtsByVect(pts,vect,colorRow)
# meshExtrudeCrvToPattern(crv,facadeType,vect)

rs.LayerVisible('genType',False)
