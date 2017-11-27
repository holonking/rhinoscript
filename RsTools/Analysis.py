import linecache
import sys
import Rhino
import rhinoscriptsyntax as rs
import RsTools.Divide as rtd

TOLERANCE = 0.0001

def equals(num1, num2, tolerance=TOLERANCE):
    if abs(num1 - num2) < tolerance:
        return True
    return False

def lists_equal(l1, l2, tolerance=TOLERANCE):
    if len(l1) != len(l2):
        return False
    for p1, p2 in zip(l1, l2):
        d = rs.Distance(p1, p2)
        if d > tolerance:
            return False
    return True

def get_shared_bisect_normal(crv, compare):
    # returns endpoint index and Vector
    # endpoint index 0=startPoint 1=endpoint
    index = None
    normal = None
    normal = get_bisect_normal_at_start(crv, compare)
    if normal is not None:
        p0 = rs.CurveStartPoint(crv)
        index = 0
        return index, normal
        # rs.AddLine(p0,p0+normal)

    normal = get_bisect_normal_at_end(crv, compare)
    if normal is not None:
        p0 = rs.CurveEndPoint(crv)
        index = 1
        return index, normal
        # rs.AddLine(p0,p0+normal)

def get_shared_bisect_Normals(crv, compares):
    # returns Vectors
    # vectors[0]=@startPoint
    # vectors[1]=@endpoint

    vectors = []

    if len(compares) == 2:
        i1, v1 = get_shared_bisect_normal(crv, compares[0])
        i2, v2 = get_shared_bisect_normal(crv, compares[1])
        if i1 == 0:
            vectors.append(v1)
            vectors.append(v2)
        else:
            vectors.append(v2)
            vectors.append(v1)
    elif len(compares) == 1:
        i1, v1 = get_shared_bisect_normal(crv, compares[0])
        if i1 == 0:
            vectors.append(v1)
            vectors.append(None)
        else:
            vectors.append(None)
            vectors.append(v1)
    else:
        vectors.append(None)
        vectors.append(None)
    return vectors

def get_bisect_normal_at_start(crv, compare):
    tolerance = 0.001
    # print('at start')
    p0 = rs.CurveStartPoint(crv)
    n1s = get_curve_plnr_normal_at_ends(crv)
    n1 = n1s[0]
    n2 = None

    # rs.AddPoint(p0)
    # print('p0:',p0)
    # print('pS:',rs.CurveStartPoint(compare))
    # print('pE:',rs.CurveEndPoint(compare))

    compStart = rs.CurveStartPoint(compare)
    compEnd = rs.CurveEndPoint(compare)

    # rs.AddLine(compStart,compStart+Point3d(0,1,0))
    # rs.AddLine(compEnd,compEnd+Point3d(0,1,0))

    n2s = get_curve_plnr_normal_at_ends(compare)
    if rs.Distance(p0, compStart) < tolerance:
        n2 = n2s[0]
        # print('found startpoint match')
    elif rs.Distance(p0, compEnd) < tolerance:
        n2 = n2s[1]
        # print('found endpoint match')
    else:
        # print('match not found')
        return None
    # rs.AddLine(p0,p0+n2)
    # rs.AddLine(p0,p0+n1)
    n = (n1 + n2) / 2
    # rs.AddLine(p0,p0+n)
    return n

def get_bisect_normal_at_end(crv, compare):
    # print('at end')
    p0 = rs.CurveEndPoint(crv)
    n1s = get_curve_plnr_normal_at_ends(crv)
    n1 = n1s[1]
    n2 = None
    #
    # rs.AddPoint(p0)
    ##print('p0:',p0)
    ##print('pS:',rs.CurveStartPoint(compare))
    ##print('pE:',rs.CurveEndPoint(compare))

    n2s = get_curve_plnr_normal_at_ends(compare)
    if p0 == rs.CurveStartPoint(compare):
        n2 = n2s[0]
        # print('found startpoint match')
    elif p0 == rs.CurveEndPoint(compare):
        n2 = n2s[1]
        # print('found endpoint match')
    else:
        return None
    # rs.AddLine(p0,p0+n2)
    # rs.AddLine(p0,p0+n1)
    n = (n1 + n2) / 2
    # rs.AddLine(p0,p0+n)
    return n

def get_curve_plnr_normal_at_ends(crv):
    up = (0, 0, 1)
    dom = rs.CurveDomain(crv)
    t0 = dom[0]
    t1 = dom[1]

    pln0 = rs.CurvePerpFrame(crv, t0)
    pln1 = rs.CurvePerpFrame(crv, t1)

    n0 = rs.VectorCrossProduct(pln0.ZAxis, up)
    n1 = rs.VectorCrossProduct(pln1.ZAxis, up)

    return n0, n1

def get_xpts_curve_circles(crv, pt, r, onlyNext=True):
    trash = []
    xc = rs.AddCircle(pt, r)
    xx = rs.CurveCurveIntersection(crv, xc)
    xpts = []
    if xx is None: return None
    # print('xx len:',len(xx))
    for xxe in xx:
        if xxe[0] == 1:
            xpts.append(xxe[1])
    rs.DeleteObject(xc)
    dom = rs.CurveDomain(crv)
    # endT=rs.CurveClosestPoint(crv,rs.CurveEndPoint(crv))
    ##print('endT :'endT)
    if onlyNext:
        centerT = rs.CurveClosestPoint(crv, pt)
        maxT = dom[0]
        maxI = 0
        for i in range(0, len(xpts)):
            p = xpts[i]
            t = rs.CurveClosestPoint(crv, p)
            if t > maxT:
                maxT = t
                maxI = i
                ##print(dom[1],centerT,t)
        if maxT > dom[1] or maxT < centerT:
            return None
        return xpts[maxI]
    return xpts

def getSrfTopBotVertCrvs(srf):
    tolerance = 0.0001
    # borders=rs.DuplicateSurfaceBorder(srf,1)
    borders = rs.DuplicateSurfaceBorder(srf)
    crvs = rs.ExplodeCurves(borders)

    hor_crvs = []
    ver_crvs = []
    trash = []
    for c in crvs:
        start = rs.CurveStartPoint(c)
        end = rs.CurveEndPoint(c)
        ##print('checking z of end points:',start[2],end[2])
        if abs(start[2] - end[2]) < tolerance:
            hor_crvs.append(c)
        elif abs(start[1] - end[1]) < tolerance and abs(start[0] - end[0]) < tolerance:
            ver_crvs.append(c)
        else:
            trash.append(c)
    ##print('hor_crvs len:',len(hor_crvs))
    hor_crvs = rs.JoinCurves(hor_crvs, True)

    bot = None
    top = None

    if len(hor_crvs) == 2:
        s1 = rs.CurveStartPoint(hor_crvs[0])
        s2 = rs.CurveStartPoint(hor_crvs[1])
        if s1[2] > s2[2]:
            bot = hor_crvs[1]
            top = hor_crvs[0]
        else:
            bot = hor_crvs[0]
            top = hor_crvs[1]

    rs.DeleteObjects(borders)
    rs.DeleteObjects(trash)

    return top, bot, ver_crvs


def getSrfHLimit(srf):
    boundary = rs.DuplicateSurfaceBorder(srf)
    pts = srf.CurveEditPoints(boundary)
    zs = []
    for p in pts: zs.append(p[2])
    zs.sort()
    top = zs[-1]
    bot = zs[0]
    return bot, top


def getAdjacentSrfs(srf, layername='CladdingDivide'):
    sel = rs.ObjectsByLayer(layername)
    srfs = []
    trash = []
    adjacent = []
    for o in sel:
        if rs.IsSurface(o):
            srfs.append(o)
    for i in range(0, len(srfs)):
        compare = srfs[i]
        if srf == compare: continue
        # action
        flag = isShareEdge(srf, compare)
        if flag: adjacent.append(compare)
        pass
    rs.DeleteObjects(trash)
    return adjacent


def isShareEdge(srf1, srf2):
    border1 = rs.DuplicateSurfaceBorder(srf1)
    border2 = rs.DuplicateSurfaceBorder(srf2)
    edges1 = rs.ExplodeCurves(border1, True)
    edges2 = rs.ExplodeCurves(border2, True)

    shareMid = []
    threshold = 0.001
    flag = False
    for e1 in edges1:
        for e2 in edges2:
            mid1 = rs.CurveMidPoint(e1)
            mid2 = rs.CurveMidPoint(e2)
            if rs.Distance(mid1, mid2) < threshold:
                s1 = rs.CurveStartPoint(e1)
                s2 = rs.CurveStartPoint(e2)
                e1 = rs.CurveEndPoint(e1)
                e2 = rs.CurveEndPoint(e2)
                if rs.Distance(s1, s1) < threshold:
                    flag = True
                    break
                if rs.Distance(s1, e1) < threshold:
                    flag = True
                    break

    rs.DeleteObjects(edges1)
    rs.DeleteObjects(edges2)
    return flag


def getVertSrf(srfs):
    vertSrfs = []
    for f in srfs:
        edges = rs.ExplodeCurves(rs.DuplicateSurfaceBorder(f), True)
        for e in edges:
            p1 = rs.CurveStartPoint(e)
            p2 = rs.CurveEndPoint(e)
            if p1[0] == p2[0] and p1[1] == p2[1]:
                vertSrfs.append(f)
                rs.DeleteObjects(edges)
                break
        rs.DeleteObjects(edges)
    return vertSrfs


def drawVectors(pts, vects, scale=3000):
    gen = []
    for p, v in zip(pts, vects):
        gen.append(rs.AddLine(p, p + rs.VectorScale(v, scale)))

    rs.AddGroup('Trash')
    rs.AddObjectsToGroup(gen, 'Trash')


def divSrfVects(srf, divWidth=900):
    # get adjacent vertical srfaces
    adj = getAdjacentSrfs(srf)
    vertSrfs = getVertSrf(adj)

    # print('len adj:',len(adj))
    # print('len verts:',len(vertSrfs))
    rs.SelectObjects(vertSrfs)

    if (len(vertSrfs) > 2):
        # print('found more than 2 adjacent surface, please check')
        # rs.SelectObjects(vertSrfs)
        return None

    top0, bot0, verts0 = getSrfTopBotVertCrvs(srf)
    top1, bot1, verts1 = getSrfTopBotVertCrvs(vertSrfs[0])
    top2, bot2, verts2 = getSrfTopBotVertCrvs(vertSrfs[1])
    poly = rtd.div_eq_crv_to_poly(bot0, w=1500, adjacentCrvs=[bot1, bot2])

    drawVectors(poly.points, poly.normals)


def isHorizonalSrf(srf, return_dir=False, tolerance=TOLERANCE):
    boundary = rs.DuplicateSurfaceBorder(srf)
    if type(boundary is list): boundary = boundary[0]
    sp = rs.CurveStartPoint(boundary)
    uv = rs.SurfaceClosestPoint(srf, sp)
    normal = rs.SurfaceNormal(srf, uv)
    normal = rs.VectorUnitize(normal)
    direct = normal[2]
    nz = abs(normal[2])
    rs.DeleteObject(boundary)
    if abs(nz - 1) < tolerance:
        if return_dir: return True, direct
        return True
    if return_dir: return False, direct
    return False


def isHorizontalUpSrf(srf, tolerance=TOLERANCE):
    boundary = rs.DuplicateSurfaceBorder(srf)
    if type(boundary is list): boundary = boundary[0]
    sp = rs.CurveStartPoint(boundary)
    uv = rs.SurfaceClosestPoint(srf, sp)
    normal = rs.SurfaceNormal(srf, uv)
    normal = rs.VectorUnitize(normal)
    nz = normal[2]
    rs.DeleteObject(boundary)
    if abs(nz - 1) < tolerance: return True
    return False
    # height=rs.CurveLength(verts[0])


def isVertical(crv, tolerance=0.0001):
    start = rs.CurveStartPoint(crv)
    end = rs.CurveEndPoint(crv)
    # if abs(start[2]-end[2])<tolerance: hor_crvs.append(c)
    if abs(start[1] - end[1]) < tolerance and abs(start[0] - end[0]) < tolerance:
        return True
    return False


def isHorizontal(crv, tolerance=0.0001):
    start = rs.CurveStartPoint(crv)
    end = rs.CurveEndPoint(crv)
    if abs(start[2] - end[2]) < tolerance:
        return True
    return False


def splitSrfBySrfs(srf, cutterSrfs):
    def split(srfs, cutter, stop=False):
        ##print('iter:{},num srfs:{}'.format(iteration,len(srfs)))
        outbin = []
        for s in srfs:
            if not rs.IsBrep(s):
                continue
            result = rs.SplitBrep(s, cutter, True)
            # print('$result is ',result)

            if result is None:
                # pass
                outbin.append(s)
            else:
                outbin += split(result, cutter)
        return outbin

    srfs = [srf]
    for i in range(0, len(cutterSrfs)):
        cutter = cutterSrfs[i]
        srfs = split(srfs, cutter)
    rs.DeleteObjects(cutterSrfs)
    return srfs


def splitSrfVerticallyByPts(srf, pts):
    normals = []
    up = (0, 0, 1000000000)
    half = (0, 0, 500000000)
    cutters = []
    for p in pts:
        uv = rs.SurfaceClosestPoint(srf, p)
        normal = rs.SurfaceNormal(srf, uv)
        normal = rs.VectorScale(normal, 1000)
        normals.append(normal)
        botStart = rs.VectorAdd(rs.VectorSubtract(p, half), normal)
        botEnd = rs.VectorSubtract(rs.VectorSubtract(p, half), normal)

        l = rs.AddLine(botStart, botEnd)
        path = rs.AddLine(botStart, rs.VectorAdd(botStart, up))
        cutter = rs.ExtrudeCurve(l, path)
        rs.DeleteObjects([l, path])

        # print(rs.IsBrep(cutter))
        # print(cutter)
        cutters.append(cutter)
    # rs.SelectObjects(cutters)
    srfs = splitSrfBySrfs(srf, cutters)
    return srfs


def splitIrregularPolygon(srf):
    boundary = rs.DuplicateSurfaceBorder(srf)
    if type(boundary) is list:
        crvs = rs.ExplodeCurves(boundary[0], False)
        rs.DeleteObjects(boundary)
    else:
        crvs = rs.ExplodeCurves(boundary, True)
    hors = []
    for c in crvs:
        if isHorizontal(c): hors.append(c)
    pts = []
    # print('hors=',hors)
    for c in hors:
        p = rs.CurveStartPoint(c)
        pts.append(p)
    rs.DeleteObjects(crvs)  #
    # print('from splitIrregularPoly ',pts)
    return splitSrfVerticallyByPts(srf, pts)