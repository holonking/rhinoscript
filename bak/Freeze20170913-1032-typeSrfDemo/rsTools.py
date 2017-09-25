import Rhino
import rhinoscriptsyntax as rs
import rsUI
reload(rsUI)


TYPECOLORS=[(0,102,204),
            (51,153,255),
            (153,204,255),
            (255,204,204),
            (255,102,102),
            (153,0,0)]


#///////////////////////////////
#//////// curve operations /////
#///////////////////////////////
def findSharedbisecNormal(crv,compare):
    #returns endpoint index and Vector
    #endpoint index 0=startPoint 1=endpoint
    index=None
    normal=None
    normal=bisecNormalAtStart(crv,compare)
    if normal is not None:
        p0=rs.CurveStartPoint(crv)
        index=0
        return index,normal
        #rs.AddLine(p0,p0+normal)

    normal=bisecNormalAtEnd(crv,compare)
    if normal is not None:
        p0=rs.CurveEndPoint(crv)
        index=1
        return index,normal
        #rs.AddLine(p0,p0+normal)
def findSharedbisecNormals(crv,compares):
    #returns Vectors
    #vectors[0]=@startPoint
    #vectors[1]=@endpoint

    vectors=[]

    if len(compares)==2:
        i1,v1=findSharedbisecNormal(crv,compares[0])
        i2,v2=findSharedbisecNormal(crv,compares[1])
        if i1==0:
            vectors.append(v1)
            vectors.append(v2)
        else:
            vectors.append(v2)
            vectors.append(v1)
    elif len(compares)==1:
        i1,v1=findSharedbisecNormal(crv,compares[0])
        if i1==0:
            vectors.append(v1)
            vectors.append(None)
        else:
            vectors.append(None)
            vectors.append(v1)
    else:
        vectors.append(None)
        vectors.append(None)
    return vectors

def divEQCrvToPolyAD(crv,w=900,adjacentCrvs=None):
    outpoly=PolyAD()
    crvLen=rs.CurveLength(crv)
    numDiv=crvLen/w
    width=crvLen/round(numDiv)
    pts=rs.DivideCurve(crv,numDiv,False,True)
        #add to output
    outpoly.points=pts

    sharedNormals=[None,None]
    if adjacentCrvs is not None:
        sharedNormals=findSharedbisecNormals(crv,adjacentCrvs)


    for i in range(0,len(pts)-2):
        up=(0,0,1)

        #     direct   direct_end
        # (p0)-v1->(p1)-v2->(p2)
        #   |n_start |n      |n_end
        #   V        V       V

        p0=pts[i]
        p1=pts[i+1]
        p2=pts[i+2]

        v1=rs.VectorUnitize(p1-p0)
        v2=rs.VectorUnitize(p2-p1)
        n1=rs.VectorCrossProduct(v1,up)
        n2=rs.VectorCrossProduct(v2,up)
        mid=rs.VectorAdd(n1,n2)
        n=rs.VectorUnitize(mid)

        direct=p1-p0
        #add to output
        outpoly.directions.append(direct)

        if i==0:
            if sharedNormals[0] is not None: n_start=sharedNormals[0]

            else: n_start=rs.VectorCrossProduct(v1,up)
            outpoly.normals.append(n_start)

        #add to output
        outpoly.normals.append(n)

        if i==len(pts)-3:
            if sharedNormals[1] is not None: n_end=sharedNormals[1]
            else: n_end=rs.VectorCrossProduct(v2,up)
            outpoly.normals.append(n_end)
            direct_end=p2-p1
            outpoly.directions.append(direct_end)




    return outpoly

def bisecNormalAtStart(crv,compare):
    tolerance=0.001
    print('at start')
    p0=rs.CurveStartPoint(crv)
    n1s=curvePlnrNormalAtEnds(crv)
    n1=n1s[0]
    n2=None

    #rs.AddPoint(p0)
    print('p0:',p0)
    print('pS:',rs.CurveStartPoint(compare))
    print('pE:',rs.CurveEndPoint(compare))

    compStart=rs.CurveStartPoint(compare)
    compEnd=rs.CurveEndPoint(compare)

    #rs.AddLine(compStart,compStart+Point3d(0,1,0))
    #rs.AddLine(compEnd,compEnd+Point3d(0,1,0))

    n2s=curvePlnrNormalAtEnds(compare)
    if rs.Distance(p0,compStart)<tolerance:
        n2=n2s[0]
        print('found startpoint match')
    elif rs.Distance(p0,compEnd)<tolerance:
        n2=n2s[1]
        print('found endpoint match')
    else :
        print('match not found')
        return None
    # rs.AddLine(p0,p0+n2)
    # rs.AddLine(p0,p0+n1)
    n=(n1+n2)/2
    #rs.AddLine(p0,p0+n)
    return n
def bisecNormalAtEnd(crv,compare):
    print('at end')
    p0=rs.CurveEndPoint(crv)
    n1s=curvePlnrNormalAtEnds(crv)
    n1=n1s[1]
    n2=None
    #
    # rs.AddPoint(p0)
    # print('p0:',p0)
    # print('pS:',rs.CurveStartPoint(compare))
    # print('pE:',rs.CurveEndPoint(compare))

    n2s=curvePlnrNormalAtEnds(compare)
    if p0==rs.CurveStartPoint(compare):
        n2=n2s[0]
        print('found startpoint match')
    elif p0==rs.CurveEndPoint(compare):
        n2=n2s[1]
        print('found endpoint match')
    else : return None
    #rs.AddLine(p0,p0+n2)
    #rs.AddLine(p0,p0+n1)
    n=(n1+n2)/2
    #rs.AddLine(p0,p0+n)
    return n
def curvePlnrNormalAtEnds(crv):
    up=(0,0,1)
    dom=rs.CurveDomain(crv)
    t0=dom[0]
    t1=dom[1]

    pln0=rs.CurvePerpFrame(crv,t0)
    pln1=rs.CurvePerpFrame(crv,t1)

    n0=rs.VectorCrossProduct(pln0.ZAxis,up)
    n1=rs.VectorCrossProduct(pln1.ZAxis,up)

    return n0,n1

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
            #print('length:',length)
            #print('rest length:',restLength)
            if length==-1:break

    if restLength>0:
        finalLength=restLength
        #print('final length:',finalLength)
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
    print(vect)
    rs.EnableRedraw(False)
    m=meshExtrudeCrvToPattern(bot,facadeType,vect)
    rs.DeleteObjects([top,bot])
    rs.DeleteObjects(verts)
    rs.EnableRedraw(True)
    return m


#///////////////////////////////
#//////// mesh operations //////
#///////////////////////////////
def addMeshQuad(verts):
    faces=[(0,1,2,3)]
    mesh=rs.AddMesh(verts,faces)
    return mesh
def meshExtrudePolyByVect(poly,vect,colorRow=None):
    pts=rs.CurveEditPoints(poly)
    meshExtrudePtsByVect(pts,vect,colorRow)

def meshExtrudePtsByVect(pts,vect,colorRow=None):
    extrudeVect=vect
    #rs.AddPoints(pts)
    meshes=[]
    #verts=[]
    #faces=[]
    for i in range(0,len(pts)-1):
        p1=pts[i]
        p2=pts[i+1]
        p1up=p1+extrudeVect
        p2up=p2+extrudeVect
        m=addMeshQuad([p1,p1up,p2up,p2])
        if colorRow is not None:
            # rs.ObjectColor(m,colorRow[i])
            rs.MeshVertexColors(m,[colorRow[i],colorRow[i],colorRow[i],colorRow[i]])
        meshes.append(m)
    mesh=rs.JoinMeshes(meshes,True)
    return mesh
def meshExtrudePolyToByVectPlane(poly,vect,pln):
    extrudeVect=vect

    #find far line from vector to be intersected later
    farvect=rs.VectorScale(extrudeVect,1000)
    pts=rs.CurveEditPoints(poly)

    meshes=[]
    for i in range(0,len(pts)-1):
        p1=pts[i]
        p2=pts[i+1]

        line=[p1,p1+farvect]
        p1pj=rs.LinePlaneIntersection(line,pln)
        line=[p2,p2+farvect]
        p2pj=rs.LinePlaneIntersection(line,pln)
        m=addMeshQuad([p1,p1pj,p2pj,p2])
        meshes.append(m)

    pjPolyPts=[]
    for p in pts:
        line=[p,p+farvect]
        xp=rs.LinePlaneIntersection(line,pln)
        pjPolyPts.append(xp)

    mesh=rs.JoinMeshes(meshes,True)
    return mesh,pjPolyPts

def meshSwipPolyAlongPolyAD(profile,polyAD):
    profile=rs.CopyObject(profile)
    pts=polyAD.points
    #TODO: finish the following function
    #the swip has to project the profile to start and end plane
    #not finished


def meshSwipPolyAlongPoly(profile,rail):
    profile=rs.CopyObject(profile)
    pts=rs.CurveEditPoints(rail)
    baseVect=Rhino.Geometry.Point3d(0,1,0)

    meshes=[]
    for i in range(0,len(pts)-2):
        p0=pts[i]
        p1=pts[i+1]
        p2=pts[i+2]

        v1=rs.VectorUnitize(p1-p0)
        v2=rs.VectorUnitize(p2-p1)
        rv1=rs.VectorUnitize(p0-p1)
        vect=p1-p0

        mid=rs.VectorUnitize((rv1+v2)/2)
        np=p1+mid
        up=p1+Rhino.Geometry.Point3d(0,0,1)
        pln=rs.PlaneFromPoints(p1,np,up)

        mesh,pjpts=meshExtrudePolyToByVectPlane(profile,vect,pln)
        meshes.append(mesh)
        rs.DeleteObject(profile)
        profile=rs.AddPolyline(pjpts)

    mesh=rs.JoinMeshes(meshes,True)
    rs.DeleteObject(profile)
    return mesh


#////////////////////////////////////
#//////// transform operations //////
#////////////////////////////////////
#orient objects along poly points
def orientObjAlongPolyPts(obj,pts,basePoint=(0,0,0),baseVect=(0,1,0)):
    print('orient obj along poly points')
    up=(0,0,1)
    generatedObjects=[]
    for i in range(0,len(pts)-1):

        if i<(len(pts)-2):
            p0=pts[i]
            p1=pts[i+1]
            p2=pts[i+2]

            v1=rs.VectorUnitize(p1-p0)
            v2=rs.VectorUnitize(p2-p1)
            n1=rs.VectorCrossProduct(v1,up)
            n2=rs.VectorCrossProduct(v2,up)
            mid=rs.VectorAdd(n1,n2)
            n=rs.VectorUnitize(mid)
        else:
            p0=pts[i]
            p1=pts[i+1]
            v1=rs.VectorUnitize(p1-p0)
            n=rs.VectorCrossProduct(v1,up)

        rs.AddLine(p1,p1+n)

        a=rs.VectorAngle((0,1,0),n)
        gen=rs.OrientObject(obj,[basePoint,basePoint+baseVect],[p1,p1+n],1)
        generatedObjects.append(gen)
        #g=rs.AddGroup()
        #groupObjects=rs.AddObjectsToGroup(generatedObjects,g)
        return generatedObjects


#////////////////////////////////////
#//////// recognitions  /////////////
#////////////////////////////////////
def getSrfTopBotVertCrvs(srf):
    tolerance=0.0001
    #borders=rs.DuplicateSurfaceBorder(srf,1)
    borders=rs.DuplicateSurfaceBorder(srf)
    crvs=rs.ExplodeCurves(borders)

    hor_crvs=[]
    ver_crvs=[]
    trash=[]
    for c in crvs:
        start=rs.CurveStartPoint(c)
        end=rs.CurveEndPoint(c)
        # print('checking z of end points:',start[2],end[2])
        if abs(start[2]-end[2])<tolerance: hor_crvs.append(c)
        elif abs(start[1]-end[1])<tolerance and abs(start[0]-end[0])<tolerance: ver_crvs.append(c)
        else: trash.append(c)
    # print('hor_crvs len:',len(hor_crvs))
    hor_crvs=rs.JoinCurves(hor_crvs,True)

    bot=None
    top=None

    if len(hor_crvs)==2:
        s1=rs.CurveStartPoint(hor_crvs[0])
        s2=rs.CurveStartPoint(hor_crvs[1])
        if s1[2]>s2[2]:
            bot=hor_crvs[1]
            top=hor_crvs[0]
        else:
            bot=hor_crvs[0]
            top=hor_crvs[1]



    rs.DeleteObjects(borders)
    rs.DeleteObjects(trash)

    return top,bot,ver_crvs
#
def getAdjacentSrfs(srf,layername='CladdingDivide'):
    sel=rs.ObjectsByLayer(layername)
    srfs=[]
    trash=[]
    adjacent=[]
    for o in sel:
        if rs.IsSurface(o):
            srfs.append(o)
    for i in range(0,len(srfs)):
        compare=srfs[i]
        if srf==compare:continue
        #action
        flag=isShareEdge(srf,compare)
        if flag:adjacent.append(compare)
        pass
    rs.DeleteObjects(trash)
    return adjacent

def isShareEdge(srf1,srf2):
    border1=rs.DuplicateSurfaceBorder(srf1)
    border2=rs.DuplicateSurfaceBorder(srf2)
    edges1=rs.ExplodeCurves(border1,True)
    edges2=rs.ExplodeCurves(border2,True)

    shareMid=[]
    threshold=0.001
    flag=False
    for e1 in edges1:
        for e2 in edges2:
            mid1=rs.CurveMidPoint(e1)
            mid2=rs.CurveMidPoint(e2)
            if rs.Distance(mid1,mid2)<threshold:
                s1=rs.CurveStartPoint(e1)
                s2=rs.CurveStartPoint(e2)
                e1=rs.CurveEndPoint(e1)
                e2=rs.CurveEndPoint(e2)
                if rs.Distance(s1,s1)<threshold:
                    flag=True
                    break
                if rs.Distance(s1,e1)<threshold:
                    flag=True
                    break

    rs.DeleteObjects(edges1)
    rs.DeleteObjects(edges2)
    return flag

def getVertSrf(srfs):
    vertSrfs=[]
    for f in srfs:
        edges=rs.ExplodeCurves(rs.DuplicateSurfaceBorder(f),True)
        for e in edges:
            p1=rs.CurveStartPoint(e)
            p2=rs.CurveEndPoint(e)
            if p1[0]==p2[0] and p1[1]==p2[1]:
                vertSrfs.append(f)
                rs.DeleteObjects(edges)
                break
        rs.DeleteObjects(edges)
    return vertSrfs

def drawVectors(pts,vects,scale=3000):
    gen=[]
    for p,v in zip(pts,vects):
        gen.append(rs.AddLine(p,p+rs.VectorScale(v,scale)))

    rs.AddGroup('Trash')
    rs.AddObjectsToGroup(gen,'Trash')



def divSrfVects(srf,divWidth=900):
    #get adjacent vertical srfaces
    adj=getAdjacentSrfs(srf)
    vertSrfs=getVertSrf(adj)

    print('len adj:',len(adj))
    print('len verts:',len(vertSrfs))
    rs.SelectObjects(vertSrfs)

    if(len(vertSrfs)>2):
        print('found more than 2 adjacent surface, please check')
        #rs.SelectObjects(vertSrfs)
        return None

    top0,bot0,verts0=getSrfTopBotVertCrvs(srf)
    top1,bot1,verts1=getSrfTopBotVertCrvs(vertSrfs[0])
    top2,bot2,verts2=getSrfTopBotVertCrvs(vertSrfs[1])
    poly=divEQCrvToPolyAD(bot0,w=1500,adjacentCrvs=[bot1,bot2])

    drawVectors(poly.points,poly.normals)


    #height=rs.CurveLength(verts[0])



#///////////////////////////////
#//////// tasks  //////
#///////////////////////////////
def importComponent(path):
    if path is None: return None
    imported=rs.Command("-Insert "+path+' Objects Enter 0,0,0 1 0')
    outComponent=AttrDict()

    if imported:
        components=rs.LastCreatedObjects()
        outComponent.polys=[]
        outComponent.breps=[]
        for comp in components:
            if rs.IsCurve(comp):outComponent.polys.append(comp)
            if rs.IsBrep(comp):outComponent.breps.append(comp)
        return outComponent
class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        # super(AttrDict, self).__init__(*args, **kwargs)
        super(dict,self).__init__(*args, **kwargs)
        self.__dict__ = self

class PolyAD(dict):
    def __init__(self, *args, **kwargs):
        super(PolyAD, self).__init__(*args, **kwargs)
        self.__dict__ = self
        self.points=[]
        self.directions=[]
        self.normals=[]
        self.perpFrames=[]

def divideCrv(crv,width):
    ds=rs.DivideCurve(crv,width,True)
    pts=[]
    for d in ds:
        pts.append(rs.IsPointOnCurve(d))
    return pts

def applyComponent(filePath,polyAD):
    trash=[]
    out=[]

    #load the component
    component=None
    try:
        component=importComponent(filPath)
    except:
        print('exception on importing module')

    if component is None:
        print('component is None, check import path')
        return None


    pts=polyAD.points
    nmls=polyAD.normals
    dirs=polyAD.directions

    #initial orientation for the component
    orientation=pts[1]-pts[0]
    for c in component.polys:
        trash.append(c)
        #mesh=meshSwipPolyAlongPoly(c,pts,numls)





class applyComponent():
    def __init__(self,uiBaseCrv,uiFileSelector):
        self.baseCrv=None
        self.baseComp=None
        self.uiBaseCrv=uiBaseCrv
        self.uiBaseCrv.bt.Click+=self.handleUIBaseCrvClicked
        self.generatedObjs=[]
        self.uiFileSelector=uiFileSelector
        self.uiFileSelector.SelectedIndexChanged+=self.handleUIFileSelected
        self.loadDirectory='/Users/holonking/Documents/Design/RhinoComponents/'
        self.loadPath='/Users/holonking/Documents/Design/RhinoComponents/component01.3dm'
    def handleUIBaseCrvClicked(self,sender,e):
        crv=rs.GetObject('select crv',4,False)
        self.uiBaseCrv.tb.Text=str(crv)
        self.baseCrv=crv
        self.update()
    def handleUIFileSelected(self,sender,e):
        txt=self.uiFileSelector.SelectedText
        self.loadPath=self.loadDirectory+txt
        print('combo select:',self.loadPath)
        self.update()

    #is update method is WIP
    #hard coded behaviors
    def update(self):
        print('update')
        #delete last generated objects
        try:
            rs.DeleteObjects(self.generatedObjs)
            self.generatedObjs=[]
        except:
            print('exception in delete generated object')

        divWidth=600
        crv=self.baseCrv
        if not rs.IsObject(crv):
            print('crv is not an object')
            return

        if not rs.IsPolyline(crv):
            pts=rs.DivideCurveEquidistant(crv,divWidth)
            rail=rs.AddPolyline(pts)
        else: rail=rs.CopyObject(crv)

        pts=rs.CurveEditPoints(rail)
        if len(pts)<3:
            print('too little points')
            return

        #find vectors to move and orient the profile
        vect=pts[1]-pts[0]
        vect=rs.VectorUnitize(vect)
        a=rs.VectorAngle(vect,(0,1,0))-90

        #load the component
        path=self.loadPath
        component=None
        try:
            component=importComponent(path)
        except:
            print('exception on importing module')


        if component is None:
            print('component is None')
            return None

        #rs.MoveObjects(component.breps,pts[0])
        #rs.RotateObjects(component.breps,pts[0],a)
        for b in component.breps:
            self.generatedObjs.append(b)
            oriented=orientObjAlongPolyPts(b,pts)
            print('pts count:',len(pts),' num gen:',len(oriented))

        rs.MoveObjects(component.polys,pts[0])
        rs.RotateObjects(component.polys,pts[0],a)
        for c in component.polys:
            self.generatedObjs.append(c)
            mesh=meshSwipPolyAlongPoly(c,rail)
            self.generatedObjs.append(mesh)
        rs.DeleteObject(rail)
        print('generated obj count:',len(self.generatedObjs))
        rs.AddGroup('gen')
        rs.AddObjectsToGroup(self.generatedObjs,'gen')
