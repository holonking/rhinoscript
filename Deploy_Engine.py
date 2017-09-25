import Rhino
import cPickle as pkl
import rhinoscriptsyntax as rs

import rsTools
reload(rsTools)
from rsTools import *

import Deploy_BaseTypes
reload(Deploy_BaseTypes)
from Deploy_BaseTypes import *

VIEWMODE=None
# PATH_PATTERN='./FacadePatterns/'
ROOT='/Users/holonking/Documents/Scripts/Rhinoscript/CladdingManagerDemo'
#PATH_PATTERN=ROOT+'/FacadePatterns/'
PATH_PATTERN='C:\\rhinoscript\\gitProject\\FacadePatterns\\'
PHASES=['BLOCK','MASSING','TYPESRF','TYPEMESH']
COLOR_SET_01=[(60,160,208),
                (255,89,25),
                (242,192,120),
                (250,237,202),
                (193,219,179),
                (126,188,137),
                (8,111,161)
                ]
COLOR_SET_02=[(0,102,204),
            (51,153,255),
            (153,204,255),
            (255,204,204),
            (255,102,102),
            (153,0,0)
            ]
DEFAULT_COLOR=(60,160,208)
PHASE_OBJECT_COLORS={
                    'BLOCK':[DEFAULT_COLOR],
                    'MASSING':[DEFAULT_COLOR],
                    'TYPESRF':[DEFAULT_COLOR],
                    'TYPEMESH':[DEFAULT_COLOR]
                    }

PHASE_OBJECT_COLORS['TYPESRF']=COLOR_SET_01
PHASE_OBJECT_COLORS['TYPEMESH']=COLOR_SET_02

LAYERNAMES=['GENBLOCK','GENMASSING','GENTYPESRF',
            'GENTYPEMESH','GENCOMPONENT']

class Engine():
    def __init__(self):

        #load data
        #self.data=self.loadData()
        self.data=None
        print('loaded data:',self.data)
        if self.data is None:
            self.importSrfTypesFromScene()
        #print('imported data:',self.data)
        print('imported data:')
        for o in self.data:
            print(o.guid)

        #load facade types
        self.loadFacadeTypes()
        #print('loaded facade types:',self.facadeTypes)

        #selection
        self.selectedItems=[]

        #layers
        self.initLayers()

    #save and load data
    def load(self):
        self.data=self.loadData()
    def loadData(self):
        #serialize the dic from a txt file
        try:
            with open('Data','rb') as fp:
                d1=pkl.load(fp)
            return d1
        except: return None
    def save(self):
        self.saveData(self.data)
    def saveData(self,data):
        try:
            filename='Data'
            with open(filename,'wb') as fp:
                pkl.dump(data,fp)
            print('engine data saved sucess')
        except:
            print('save faile failed')

    #object life cycle managements
    def addObject(self,guid,phaseIndex,typeIndex,upStream,description='',needUpdate=False):
        o=PhaseObject()
        o.guid=guid
        o.phase=phaseIndex
        o.typeIndex=typeIndex
        o.upStream=upStream
        o.description=description
        o.needUpdate=needUpdate
        upStream.downStream.append(o)
        # print('added o:',o.phase,o.typeIndex)
        self.data.append(o)
    def deleteObject(self,obj):
        if obj is None: return None
        print('delete object')
        print('---',obj.guid)
        print('---',obj.phase)
        print('---',obj.typeIndex)
        print('---',obj.upStream)
        if rs.IsObject(obj.guid): rs.DeleteObject(obj.guid)
        upStream=obj.upStream
        self.inspectObject(upStream.guid)
        try:#delete the object from upStream
            index=upStream.downStream.index(obj)
            if index>=0: del upStream[index]
        except Exception as e:print('!except at deleteOjbect() 1',e)

        try:#delete the object from data
            index=self.data.index(obj)
            if index>=0: del self.data[index]
        except Exception as e:print('!except at deleteOjbect() 2',e)
        return upStream
    def deleteObjects(self,phaseIndex,typeIndex=None):
        #deletes a phase object and returns upStream
        upStream=None
        trashGuid=[]
        updatedList=[]
        # print('before delete, self.data size:',len(self.data))

        for o in self.data :
            # print('@del ',o.phase,o.typeIndex,':',typeIndex)
            if o.phase==phaseIndex:
                if typeIndex is None: flag=True
                elif typeIndex ==o.typeIndex: flag=True
                else: flag=False
                if flag:
                    # print('found type index match')
                    if rs.IsObject(o.guid):
                        trashGuid.append(o.guid)
                        upStream=o.upStream
                        try:#delete the object from upStream
                            index=upStream.downStream.index(o)
                            if index>=0: del upStream[index]
                        except Exception as e:print('except inside del ',e)
                else:
                    updatedList.append(o)
                #end if flag
            else:
                updatedList.append(o)
            #end for o.phase
        # print('updated list size:',updatedList)
        self.data=updatedList
        if len(trashGuid)>0:
            # print('delteing ',len(trashGuid),' objects')
            # print('..........................')
            rs.DeleteObjects(trashGuid)
        return upStream

    #selection management
    def clearSelections(self):
        self.selectedItems=[]
    def addToSelection(self,items):
        for i in items:
            self.selectedItems.append(i)
    def setSelection(self,items):
        self.selectedItems=items
    def highlightSelection(self):
        rs.UnselectAllObjects()
        guids=self.getGuidFromADs(self.selectedItems)
        rs.SelectObjects(guids)

    #data query and inspections
    def inspectObject(self,guid):
        for o in self.data:
            if o.guid==guid:
                print('<-----INSPECT OBJCT------->')
                print('<-----guid :',o.guid)
                print('<-----phase:',o.phase)
                print('<-----typeI:',o.typeIndex)
                print('<-----upStm:',o.upStream)
                print('<-----dnStm:',o.downStream)
                print('<-----dsrpt:',o.description)
                print('down stream objects:')
                for o in o.downStream:
                    print(o.guid)
                break
    def getGuidFromADs(self,oAD):
        guids=[]
        for o in oAD:
            guids.append(o.guid)
        return guids
    def getObjectPhaseObject(self,obj,phase):
        #finds the object's up or down stream objects
        phase1=obj.phase
        phase2=phase
        i1=PHASES.index(phase1)
        i2=PHASES.index(phase2)
        direction=self.streamDirection(phase1,phase2)
        selection=[]
        if direction==0: return obj
        # stop=i2+direction
        while not i1==i2:
            i1+=direction
            selection+=obj.downStream
        return selection
    def streamDirection(self,phase1,phase2):
        #determin the direction of phase 2 compares to phase 1
        # -1=upStream, 1=downStream, 0=same phase
        if phase1==phase2:return 0
        i1=PHASES.index(phase1)
        i2=PHASES.index(phase2)
        if i2<i1: return -1
        else: return 1
    def getObjectByGuid(self,guid):
        for o in self.data:
            if o.guid==guid: return o,o.upStream
    def getObject(self,phaseIndex,typeIndex=None):
        selection=[]
        for o in self.data:
            #print('@getObject',o.phase,phaseIndex)
            if o.phase==phaseIndex:
                if typeIndex is None: flag=True
                elif typeIndex==o.typeIndex: flag=True
                else: flag=False
                if flag: selection.append(o)
        return selection

    #layer managements
    def initLayers(self):
        for n in LAYERNAMES:
            rs.AddLayer(n,locked=True)
    def isolateLayer(self,layerName):
        names=rs.LayerNames()
        rs.CurrentLayer('Default')
        for n in names:
            if n=='Default':continue
            if n==layerName:
                layers=rs.LayerVisible(layerName,True)
            else:rs.LayerVisible(n,False)

    #object generators
    def genTypeMeshObject(self,obj):

        facadeType=self.facadeTypes[obj.typeIndex]
        downStream=obj.downStream
        layerName='GENTYPEMESH'
        phaseIndex='TYPEMESH'
        print('!!! downStrem size:',len(downStream))
        print(downStream)
        for ds in downStream:
            self.deleteObject(ds)
            #pass
        try:
            m=divideSrfToPattern(obj.guid,facadeType)
            if rs.IsObject(m):
                rs.ObjectLayer(m,layerName)
                self.addObject(m,phaseIndex,obj.typeIndex,obj)
        except Exception as e:
            print('exception in divideSrfToPattern:',Exception,':',e)
            rs.EnableRedraw(True)
        pass
    def genTypeMesh(self,typeIndex=None):
        #if not typeIndex given, will regenerate all types
        meshes=[]
        srfs=[]
        updatedList=[]
        phaseIndex='TYPEMESH'
        upStreamIndex='TYPESRF'
        layerName='GENTYPEMESH'
        #remove existing mesh
        try:
            self.deleteObjects(phaseIndex,typeIndex)
        except Exception as e:print('except at delete :',e)

        #find all the TYPESRF
        try:
            srfs=self.getObject(upStreamIndex,typeIndex)
        except Exception as e: print('except genTypeMesh->self.getObject:',e)
        for o  in srfs:
            if typeIndex is not None:
                if not o.typeIndex==typeIndex: continue

            #typeI=typeIndex%len(self.facadeTypes)
            typeI=o.typeIndex
            #print('typeI:',typeI,self.facadeTypes)
            try:
                facadeType=self.facadeTypes[typeI]
                #print('facade type: ',facadeType)
            except Exception as e:
                print('exception in getting self.facadeTypes',e)
                return
            try:
                m=divideSrfToPattern(o.guid,facadeType)
                if rs.IsObject(m):
                    rs.ObjectLayer(m,layerName)
                    self.addObject(m,phaseIndex,typeI,o)
            except Exception as e:
                print('exception in divideSrfToPattern:',Exception,':',e)
                rs.EnableRedraw(True)
        #generate new mesh
    def genAllTypeMesh(self,sender,e):
        self.genTypeMesh()

    #checked "self."
    #library and static variables managements
    def loadFacadeTypes(self):
        facadeTypes=[]
        import os
        #directory='./FacadePatterns/'
        #directory='C:\\rhinoscript\\gitProject\\FacadePatterns\\'
        directory=self.getPathPattern()
        files=os.listdir(directory)
        for f in files:
            if f.find('.facade')>0:
                filename=directory+f
                print(filename)
                #for mac use 'rb'
                #with open(filename,'rb') as fp:
                with open(filename,'r') as fp:
                    #for line in fp:
                    #    print(line)
                    facadeTypes.append(pkl.load(fp))

        self.facadeTypes=facadeTypes
    def updateFacadeType(self,typeIndex,filename):
        directory=PATH_PATTERN
        filename=directory+filename
        print('file name @ updateFacadeType: ',filename)
        with open(filename,'rb') as fp:
            facade=pkl.load(fp)
        self.facadeTypes[typeIndex]=facade
        print('facade type:',i,'is updated to ',filename)
        for t in self.facadeTypes:
            print(t)
    def get_color(self,phase,index):
        colors=PHASE_OBJECT_COLORS['TYPESRF']
        index=index%len(colors)
        return SRFTYPECOLORS[index]
    def getPathPattern(self):
        return PATH_PATTERN



    #assign UI actions
    def assignAction(self,form):
        #engine.importSrfTypesFromScene()

        self.form=form
        form.Closing +=self.onFormCloseEvents

        #assign GENBLOCK button actions
        form.UI_GENBLOCK.bt_view_block.Click+=self.handle_GENBLOCK_bt_view_block
        form.UI_GENBLOCK.bt_view_srf.Click+=self.handle_GENBLOCK_bt_view_srf

        #assign GENTYPESRF button actions
        form.UI_GENTYPESRF.bt_regen.Click+=self.genAllTypeMesh
        form.UI_GENTYPESRF.bt_view_srf.Click+=self.handle_GENTYPESRF_bt_viewSrf
        form.UI_GENTYPESRF.bt_view_mesh.Click+=self.handle_GENTYPESRF_bt_viewMesh
        form.UI_GENTYPESRF.bt_inspect.Click+=self.handle_GENTYPESRF_bt_inspect
        self.loadRhinoEvents()

        self.handle_GENTYPESRF_bts1()
        self.handle_GENTYPESRF_bts2()
        self.handle_GENTYPESRF_comboBox()
    def loadRhinoEvents(self):
        Rhino.RhinoDoc.EndSaveDocument+=self.saveEngineData
        Rhino.RhinoDoc.SelectObjects+=self.onSelectObjects
    def unloadRhinoEvents(self):
        Rhino.RhinoDoc.EndSaveDocument-=self.saveEngineData
        Rhino.RhinoDoc.SelectObjects-=self.onSelectObjects
    def saveEngineData(self,sender,e):
        self.save()
    def onFormCloseEvents(self,sender,e):
        self.save()
        self.unloadRhinoEvents()
        print('save data and unload Rhino events')
    def onSelectObjects(self,sender,e):
        #find selection in current data
        pass
    def handle_GENTYPESRF_bt_viewSrf(self,sender,e):
        print('view srf clicked')
        global VIEWMODE
        VIEWMODE='TYPESRF'
        self.isolateLayer('GENTYPESRF')
        self.highlightSelection()
        #self.viewMode_srfType='SRF'
    def handle_GENTYPESRF_bt_viewMesh(self,sender,e):
        print('view mesh clicked')
        global VIEWMODE
        VIEWMODE='TYPESRF'
        self.isolateLayer('GENTYPEMESH')
        self.highlightSelection()

    def handle_GENTYPESRF_bt_inspect(self,sender,e):
        obj=rs.GetObject('sel obj to inspect')
        if obj is None:
            print('nothing selected')
            return
        self.inspectObject(obj)
    def handle_GENTYPESRF_bts1(self):
        form=self.form
        bts=form.UI_GENTYPESRF.bts1
        # print(bts)
        class handleBt1():
            def __init__(self,i,engine):
                self.index=i
                self.engine=engine
                self.toggle=False
            def handle(self,sender,e):
                if not self.toggle:
                    self.toggle=True
                    rs.UnselectAllObjects()
                    self.engine.clearSelections()
                    selection=[]

                    #print('handle bt 1:',self.index)

                    for o in self.engine.data:
                        # print('bt1 Click:',o.typeIndex,self.index,o.guid)
                        if o.typeIndex==self.index:
                            # print('selected')
                            try:
                                if rs.IsObject(o.guid):
                                    selection.append(o)
                            except Exception as e: print('!except handleBt1 sselect ',e)

                    # print('bt1 Click selection size :',len(selection))
                    self.engine.setSelection(selection)
                    self.engine.highlightSelection()
                else:
                    self.toggle=False
                    self.engine.setSelection([])
                    rs.UnselectAllObjects()


        for i in range(0,len(bts)):
            bt=bts[i]
            handler=handleBt1(i,self)
            bt.Click+=handler.handle
    def handle_GENTYPESRF_bts2(self):
        form=self.form
        #handle the second button which sets srf to a type
        bts=form.UI_GENTYPESRF.bts2
        # print(bts)
        class handleBt2():
            def __init__(self,i,engine):
                self.index=i
                self.engine=engine
            def handle(self,sender,e):
                try:
                    rs.UnselectAllObjects()
                    self.engine.clearSelections()

                    objs=rs.SelectedObjects()
                    if len(objs)==0:
                        objs=rs.GetObjects('select obj to change type, and press enter')

                    #case of mesh view
                    for ro in objs:
                        po,upStream=self.engine.getObjectByGuid(ro)
                        upStream.typeIndex=self.index
                        rs.ObjectColor(upStream.guid,SRFTYPECOLORS[self.index])
                        #TODO:the following line deleted upstream from engine
                        #TODO:color is not updating
                        # self.engine.genTypeMeshObject(upStream)
                except Exception as e: print(e)

        for i in range(0,len(bts)):
            bt=bts[i]
            handler=handleBt2(i,self)
            bt.Click+=handler.handle
    def handle_GENTYPESRF_comboBox(self):
        form=self.form
        combos=form.UI_GENTYPESRF.combos
        class handleComboBox():
            def __init__(self,i,engine,combo):
                self.index=i
                self.combo=combo
                self.engine=engine
            def handle(self,sender,arg):
                try:
                    selIndex=self.combo.SelectedIndex
                    filename=self.combo.Items[selIndex]

                    print('combo box index changed to ',selIndex,filename.Text)
                    self.engine.updateFacadeType(self.index,filename.Text)
                except Exception as e:print('before genTypeMesh',e)
                try:
                    self.engine.genTypeMesh(self.index)
                except Exception as e:
                    print('@ handle combo change',Exception,':',e)

        for i in range(0,len(combos)):
            combo=combos[i]
            handler=handleComboBox(i,self,combo)
            combo.SelectedIndexChanged+=handler.handle
        #SelectedIndexChanged

    def handle_GENBLOCK_bt_view_block(self,sender,e):
        self.isolateLayer('GENBLOCK')
    def handle_GENBLOCK_bt_view_srf(self,sender,e):
        layername='GENMASSING'
        tolerance=0.0001
        self.isolateLayer(layername)
        rs.DeleteObjects(rs.ObjectsByLayer(layername))
        rs.CurrentLayer(layername)
        # objs=[]
        blocks=rs.ObjectsByLayer('GENBLOCK')
        # rs.SelectObjects(blocks)
        blocks=rs.CopyObjects(blocks)
        blocks=rs.BooleanUnion(blocks,True)

        splitedSrfs=[]
        for b in blocks:
            os=rs.ExplodePolysurfaces(b,True)
            for s in os:
                boundary=rs.DuplicateSurfaceBorder(s)
                pts=rs.CurveEditPoints(boundary)
                if len(pts)>5:
                    print('splitting polygon')
                    srfs=spliteIrregularPolygon(s)
                    splitedSrfs+=srfs
                else: splitedSrfs.append(s)
                rs.DeleteObject(boundary)

        # whs=[]
        # taken=[False]*len(splitedSrfs)
        # joinedSrfs=[]
        # for i in range(0,len(splitedSrfs)):
        #     s1=splitedSrfs[i]
        #     if taken[i]:continue
        #     taken[i]=True
        #     joinedSrf=rs.CopyObject(s1)
        #     for j in range(0,len(splitedSrfs)):
        #         if i==j :continue
        #         s2=splitedSrfs[j]
        #         top1,bot1,verts1=getSrfTopBotVertCrvs(s1)
        #         top2,bot2,verts2=getSrfTopBotVertCrvs(s2)
        #         topDiff=abs(top1[2]-top2[2])
        #         botDiff=abs(bot1[2]-bot2[2])
        #         if topDiff<tolerance and botDiff<tolerance:
        #             result=rs.JoinSurfaces([joinedSrf,s2])
        #             if result is None:
        #                 continue
        #             else:
        #                 joinedSrf=result
        #                 taken[j]=True
        #         #end if
        #     #end for j
        #     joinedSrfs.append(joinedSrf)
        #     rs.DeleteObjects(splitedSrfs)
        #     #TODO:delete splitedSrfs



    #update phase object rhino properties
    def updatePhaseObjectColor(self,obj):

        phase=obj.phase
        index=obj.typeIndex
        colors=PHASE_OBJECT_COLORS[phase]
        colorIndex=index%len(colors)
        color=colors[colorIndex]
        print('@updateColor:',color,obj.guid)
        rs.ObjectColor(obj.guid,color)
        #TODO:return the color PHASE_OBJECT_COLORS[phase][typeIndex]

    #existing model treatments
    def importSrfTypesFromScene(self):

        data=[]
        srfs=rs.ObjectsByLayer('GENTYPESRF')
        for f in srfs:
            #rs.SelectObject(f)
            #rs.ObjectColor(f,(0,0,1))
            po=PhaseObject()
            po.guid=f
            po.phase='TYPESRF'
            po.typeIndex=int(rs.ObjectName(f))
            po.strTypeDescription=rs.ObjectName(f)
            self.updatePhaseObjectColor(po)
            data.append(po)
        self.data=data

        objs=rs.ObjectsByLayer('GENBLOCK')
        for o in objs:
            po=PhaseObject()
            po.guid=o
            po.phase='BLOCK'
            po.typeIndex=0
            po.strTypeDescription=rs.ObjectName(f)
            self.updatePhaseObjectColor(po)
            data.append(po)

    # def fixCurrentModel(self):
    #     #fix srf in current scene
    #     layer='GENTYPESRF'
    #     srfs=rs.ObjectsByLayer(layer)
    #     counter=0
    #     global SRFTYPECOLORS
    #     for f in srfs:
    #         rs.ObjectLayer(f,layer)
    #         typeindex=int(rs.ObjectName(f))
    #         index=typeindex%len(SRFTYPECOLORS)
    #         color=SRFTYPECOLORS[index]
    #         rs.ObjectColor(f,color)
    #         counter+=1
