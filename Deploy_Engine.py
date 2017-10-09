
# -*- coding: utf-8 -*-
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
import os
#check which OS system, if nt, means windows
if os.name=='nt':
    PATH_PATTERN='C:\\Users\\31720\\Design\\Rhinoscript\\rhinoscript\\FacadePatterns\\'
else:
    PATH_PATTERN='./FacadePatterns/'

PHASES=['BLOCK','MASSING','MASSINGSPLIT','TYPESRF','TYPEMESH','COMPONENTS']
def get_layer_name(phase):
    return '$AGL_'+phase

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
                    'MASSINGSPLIT':[DEFAULT_COLOR],
                    'TYPESRF':[DEFAULT_COLOR],
                    'TYPEMESH':[DEFAULT_COLOR]
                    }
PHASE_OBJECT_COLORS['BLOCK']=COLOR_SET_01
PHASE_OBJECT_COLORS['TYPESRF']=COLOR_SET_01
PHASE_OBJECT_COLORS['TYPEMESH']=COLOR_SET_02

class Engine():
    def __init__(self):

        #propagate required layers
        for phase in PHASES:
            lay=get_layer_name(phase)
            if not rs.IsLayer(lay):rs.AddLayer(lay)


        #load data
        #self.data=self.loadData()
        self.data=PhaseObject(phase='Root')

        #print('loaded data:',self.data)
        #if self.data is None:
            #self.importSrfTypesFromScene()

        #print('imported data:',self.data)
        #print('imported data:')
        #for o in self.data:
        #    print(o.guid)

        #load facade types
        self.loadFacadeTypes()
        #print('loaded facade types:',self.facadeTypes)

        #loggin panel passed from UI
        self.log_panel=None

        #selection
        self.selectedObjects=[]
        self.selectedObject=None
        self.selectedRhiObjects=[]
        self.selectedRhiObject=None
        #layers
        self.initLayers()

        #interaction modes
        self.interaction_mode=AttrDict()
        self.interaction_mode.auto_block=True

    def suspendInteraction(self):
        self.interaction_mode.auto_block=False
    def resumeInteraction(self):
        self.interaction_mode.auto_block=True

    def logDataTree(self):
        #if len(self.data)==0:return
        #txt='DATA SIZE:'+str(len(self.data))+'\n'
        txt=''
        txt+=self.data.tree()
        # for po in self.data:
        #     if po.is_root():
        #         txt+=po.tree()
        self.logToTreePanel(txt)
    def logToTreePanel(self,txt):
        if self.log_tree_panel is None:
            print('engine.log_panel not set')
            return
        else: self.log_tree_panel.Text=txt
    def logToObjPanel(self,txt):
        if self.log_obj_panel is None:
            print('engine.log_obj_panel not set')
            return
        else: self.log_obj_panel.Text=txt
    def logToRhiPanel(self,txt):
        if self.log_rhi_panel is None:
            print('engine.log_panel not set')
            return
        else: self.log_rhi_panel.Text=txt
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


    def addObject(self,guid,phase,typeIndex,parent=None,description='',needUpdate=False):
        #print('add object ',shortGuid(guid))
        if self.data.find('guid',guid):
            print('obj exists in data')
            return None

        o=PhaseObject()
        o.guid=guid
        o.phase=phase
        o.typeIndex=typeIndex
        o.set_parent(parent)
        o.description=description
        o.needUpdate=needUpdate
        #parent.add_child(o)
        rs.ObjectColor(guid,self.get_color(phase,typeIndex))
        self.data.add_child(o)
        self.logDataTree()
        return o

    def deleteObjectsByGuid(self,guids):
        # print('deleteObjectsByGuid')
        # otd=[]
        for guid in guids:
            o=self.data.find('guid',guid)
            if o is not None:
                o.delete()
        self.logDataTree()


    def deleteObjectByGuid(self,guid):
        print('deleteObjectsByGuid')

        o=self.data.find('guid',guid)
        print('DELETED OBJ',o)
        if o is not None:
            o.delete()

        self.logDataTree()

    def deleteObject(self,obj):
        if obj is None: return None
        #if rs.IsObject(obj.guid): rs.DeleteObject(obj.guid)
        obj.delete()
    def deleteObjects(self,phase,typeIndex=None):
        #deletes objects off the same phase and type index
        #<to be confirmed>
        cons=[('phase',phase),('typeIndex',typeIndex)]
        fos=self.data.find_all(cons)
        for o in fos:
            o.delete()

    #selection management
    def clearSelections(self):
        self.selectedObjects=[]
    def addToSelection(self,items):
        for i in items:
            self.selectedObjects.append(i)
    def setSelection(self,items):
        self.selectedObjects=items
    def highlightSelection(self):
        rs.UnselectAllObjects()
        guids=self.getGuidFromADs(self.selectedObjects)
        rs.SelectObjects(guids)

    #data query and inspections
    def inspectObject(self,guid):
        try:
            txt=''
            for o in self.data.flattern():
                if o.guid==guid:
                    txt+='guid :'+shortGuid(o.guid)+'\n'
                    txt+='phase:'+str(o.phase)+'\n'
                    txt+='typeI:'+str(o.typeIndex)+'\n'
                    txt+='typeIS:['
                    for i in o.typeIndices:
                        txt+=str(i)+','
                    txt+=']\n'
                    if o.parent is not None:
                        txt+='upStm:'+shortGuid(o.parent.guid)+'\n'
                    else:
                        txt+='upStm:'+'None\n'
                    txt+='dnStm:'
                    for c in o.children:
                        txt+=shortGuid(c.guid)+' '
                    txt+='\n'
                    txt+='dsrpt:'+o.description+'\n'
                    #txt+='down stream objects:\n'
                    #for o in o.children:
                    #    txt+=shortGuid(o.guid)+'\n'
                    break
            #print(txt)
            return txt
        except:PrintException()
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
            selection+=obj.children
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
            if o.guid==guid: return o
        return None#,o.parent
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
    def setObjectType(self,obj,typeIndex=0,index=None):
        colorI=int(typeIndex)%len(COLOR_SET_01)
        color=COLOR_SET_01[colorI]
        rs.ObjectColor(obj.guid,color)
        if index is None:
            obj.typeIndex=int(typeIndex)
        else:
            obj.typeIndices[int(index)]=typeIndex

    #layer managements
    def initLayers(self):
        #propagate required layers
        parent=get_layer_name('LOCKEDLAYERS')
        rs.AddLayer(get_layer_name('LOCKEDLAYERS'),locked=False)
        for phase in PHASES:
            lay=get_layer_name(phase)
            if not rs.IsLayer(lay):rs.AddLayer(lay,locked=False)
            else: rs.LayerLocked(lay,False)
            #rs.ParentLayer(lay,parent)
        rs.ExpandLayer(parent,False)

    def isolateLayer(self,layerName):
        names=rs.LayerNames()
        rs.CurrentLayer('Default')
        for n in names:
            if n=='Default':continue
            if n==get_layer_name('LOCKEDLAYERS'):
                rs.LayerVisible(layerName,True)
                continue
            if n==layerName:
                layers=rs.LayerVisible(layerName,True)
            else:rs.LayerVisible(n,False)

    #object generators
    def genTypeMeshObject(self,obj):

        facadeType=self.facadeTypes[obj.typeIndex]
        downStream=obj.children
        layerName=get_layer_name('TYPEMESH')
        phaseIndex='TYPEMESH'
        #print('!!! downStrem size:',len(downStream))
        #print(downStream)
        for ds in downStream:
            self.deleteObject(ds)
            #pass
        try:
            m=divideSrfToPattern(obj.guid,facadeType)
            if rs.IsObject(m):
                rs.ObjectLayer(m,layerName)
                self.addObject(m,phaseIndex,obj.typeIndex,obj)
        except Exception as e:
            #print('exception in divideSrfToPattern:',Exception,':',e)
            PrintException()
            rs.EnableRedraw(True)
        pass
    def genTypeMesh(self,typeIndex=None):
        #if not typeIndex given, will regenerate all types
        rs.EnableRedraw(False)
        meshes=[]
        srfs=[]
        updatedList=[]
        phaseIndex='TYPEMESH'
        upStreamIndex='TYPESRF'
        layerName=get_layer_name('TYPEMESH')
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
                #rs.EnableRedraw(True)
                return
            try:
                m=divideSrfToPattern(o.guid,facadeType)
                if rs.IsObject(m):
                    rs.ObjectLayer(m,layerName)
                    self.addObject(m,phaseIndex,typeI,o)
            except Exception as e:
                #rs.EnableRedraw(True)
                print('exception in divideSrfToPattern:',Exception,':',e)
                #rs.EnableRedraw(True)
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
        print(directory)
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
        from System.IO import Directory, Path
        #directory = Directory.GetCurrentDirectory()
        #filename = Path.Combine(directory, filename)
        directory=PATH_PATTERN
        filename=directory+filename
        #filename='.\\'+filename

        print('file name @ updateFacadeType: ',filename)
        try:
            with open(filename,'r' ) as fp:
                facade=pkl.load(fp)
        except:
            PrintException()

        self.facadeTypes[typeIndex]=facade
        for t in self.facadeTypes:
            print(t)
    def get_color_default(self):
        return DEFAULT_COLOR
    def get_color_set1(self,index):
        return COLOR_SET_01[index%len(COLOR_SET_01)]
    def get_color(self,phase='BLOCK',index=0):
        colors=PHASE_OBJECT_COLORS[phase]
        index=index%len(colors)
        color=colors[index]
        return color
    def get_colors(self,phase,index):
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
        form.UI_GENBLOCK.bt_interact.Click+=self.handle_GENBLOCK_bt_interact
        form.UI_GENBLOCK.combo_typeIndex1.SelectedIndexChanged+=self.handle_GENBLOCK_combo_updates
        form.UI_GENBLOCK.combo_typeIndex2.SelectedIndexChanged+=self.handle_GENBLOCK_combo_updates
        form.UI_GENBLOCK.combo_typeTopIndex.SelectedIndexChanged+=self.handle_GENBLOCK_combo_updates

        #assign GENTYPESRF button actions
        form.UI_GENTYPESRF.bt_regen.Click+=self.genAllTypeMesh
        form.UI_GENTYPESRF.bt_view_srf.Click+=self.handle_GENTYPESRF_bt_viewSrf
        form.UI_GENTYPESRF.bt_view_mesh.Click+=self.handle_GENTYPESRF_bt_viewMesh
        form.UI_GENTYPESRF.bt_inspect.Click+=self.handle_GENTYPESRF_bt_inspect

        self.loadRhinoEvents()

        self.handle_GENTYPESRF_bts1()
        self.handle_GENTYPESRF_bts2()
        self.handle_GENTYPESRF_comboBox()

        self.log_tree_panel=form.treeTextBox
        self.log_obj_panel=form.objTextBox
        self.log_rhi_panel=form.rhiTextBox

        #TOOBAR action assignment
        form.UI_TOOLBAR.bt_delete.Click+=self.handle_TOOLBAR_bt_delete

        self.logDataTree()

    def loadRhinoEvents(self):
        print('loading rhino events')
        Rhino.RhinoDoc.EndSaveDocument+=self.saveEngineData
        Rhino.RhinoDoc.SelectObjects+=self.onSelectObjects
        Rhino.RhinoDoc.AddRhinoObject+=self.onAddRhinoObject
        Rhino.RhinoDoc.DeleteRhinoObject+=self.onDeleteRhinoObject

    def unloadRhinoEvents(self):
        Rhino.RhinoDoc.EndSaveDocument-=self.saveEngineData
        Rhino.RhinoDoc.SelectObjects-=self.onSelectObjects
        Rhino.RhinoDoc.AddRhinoObject-=self.onAddRhinoObject
        Rhino.RhinoDoc.DeleteRhinoObject-=self.onDeleteRhinoObject
    def saveEngineData(self,sender,e):
        self.save()
    def onDeleteRhinoObject(self,sender,e):
        #do not impliment
        #it will be called even when moving an object
        #if you want to delete an object, please use the UI delete button
        pass

    def onAddRhinoObject(self,sender,e):
        obj=rs.FirstObject()
        isBrep=rs.IsBrep(obj)
        if self.interaction_mode.auto_block and isBrep:
            self.addObject(obj,'BLOCK',0,None)

    def onFormCloseEvents(self,sender,e):
        self.save()
        self.unloadRhinoEvents()
        print('save data and unload Rhino events')
    def onSelectObjects(self,sender,e):
        try:
            sel=rs.SelectedObjects()
            self.selectedRhiObjects=sel
            txt='sel '+str(len(sel))+':'


            for o in sel:
                txt+=shortGuid(o)+','
            #print(txt)
            self.logToRhiPanel(txt)
            if len(sel)==0:
                self.selectedRhiObject=None
                self.selectedObject=None
                self.form.UI_GENBLOCK.lb_selected_block.Text='Select block to edit'
            if len(sel)==1:
                guid=sel[0]
                self.selectedRhiObject=guid
                txt=self.inspectObject(guid)
                self.logToObjPanel(txt)
                #obj=self.getObjectByGuid(guid)
                obj=None
                for po in self.data.flattern():
                    if po.guid==guid:
                        obj=po
                        po.is_selected=True
                    else: po.is_selected=False
                if obj is not None:
                    self.selectedObject=obj
                    #try to update the block panel
                    if obj.phase=='BLOCK':
                        self.update_GENBLOCK_PROPS()
                self.logDataTree()
        except:
            PrintException()
        #find selection in current data
    def setComboIndexfromItem(self,combo,item):
        index=0
        #print(combo,item)
        index=0
        try:
            index=combo.Items.index(item)
        except:pass
        #combo.SelectedIndex=index
        combo.Text=str(item)

    def update_GENBLOCK_PROPS(self):
        try:
            clear=False
            if self.selectedObject is None: clear=True
            elif self.selectedObject.phase!='BLOCK': clear=True
            if clear:
                self.form.UI_GENBLOCK.lb_selected_block.Text='Select Block to edit'
                self.form.UI_GENBLOCK.combo_typeIndex1.SelectedIndex=0
                self.form.UI_GENBLOCK.combo_typeIndex2.SelectedIndex=0
                self.form.UI_GENBLOCK.combo_typeTopIndex.SelectedIndex=0
            else:
                obj=self.selectedObject
                self.form.UI_GENBLOCK.lb_selected_block.Text='Editing '+shortGuid(obj.guid)
                self.setComboIndexfromItem(self.form.UI_GENBLOCK.combo_typeIndex1,obj.typeIndices[0])
                self.setComboIndexfromItem(self.form.UI_GENBLOCK.combo_typeIndex2,obj.typeIndices[1])
                self.setComboIndexfromItem(self.form.UI_GENBLOCK.combo_typeTopIndex,obj.typeIndices[2])
        except:PrintException()

    def handle_TOOLBAR_bt_delete(self,sender,e):
        print('del pressed')
        if self.selectedObject:
            print('deleting:',self.selectedObject.to_string())
            self.selectedObject.delete()
        self.logDataTree()

    def handle_GENTYPESRF_bt_viewSrf(self,sender,e):
        print('view srf clicked')
        global VIEWMODE
        VIEWMODE='TYPESRF'
        self.isolateLayer(get_layer_name('TYPESRF'))
        self.highlightSelection()
        #self.viewMode_srfType='SRF'
    def handle_GENBLOCK_bt_interact(self,sender,e):
        try:
            if self.interaction_mode.auto_block:
                self.form.UI_GENBLOCK.bt_interact.Text='-Intr'
                self.interaction_mode.auto_block=False
            else:
                self.form.UI_GENBLOCK.bt_interact.Text='+Intr'
                self.interaction_mode.auto_block=True
        except: PrintException()

    def handle_GENTYPESRF_bt_viewMesh(self,sender,e):
        print('view mesh clicked')
        global VIEWMODE
        VIEWMODE='TYPESRF'
        self.isolateLayer(get_layer_name('TYPEMESH'))
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

        from Eto.Drawing import Color
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
                except Exception :PrintException()
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
        self.isolateLayer(get_layer_name('BLOCK'))
    def handle_GENBLOCK_bt_view_srf(self,sender,e):
        self.suspendInteraction()
        rs.EnableRedraw(False)
        try:
            layername=get_layer_name('MASSING')
            tolerance=0.0001
            self.isolateLayer(layername)
            sel=rs.ObjectsByLayer(layername)
            print('sel from MASSING layer:',sel)
            self.deleteObjectsByGuid(sel)
            rs.CurrentLayer(layername)

            blocks=rs.ObjectsByLayer(get_layer_name('BLOCK'))
            cblocks=rs.CopyObjects(blocks)
            ublocks=rs.BooleanUnion(cblocks,True)

            splitedSrfs=[]
            horzSrfs=[]
            vertSrfs=[]

            #找出union block里的横竖面
            print('Sparate horz and vert srfs')
            for b in ublocks:
                os=rs.ExplodePolysurfaces(b,True)
                #先把水平面分走
                horzSrfs=[]
                vertSrfs=[]

                for s in os:
                    if s is None: continue
                    if not rs.IsObject(s): continue
                    isHor,direct=isHorizonalSrf(s,True)
                    if isHorizonalSrf(s):
                        if direct<0:
                            rs.ObjectColor(s,(255,0,0))
                        else:
                            rs.ObjectColor(s,COLOR_SET_01[5])
                        horzSrfs.append(s)
                    else : vertSrfs.append(s)

            blockedSrf=[]
            parentDic={}
            wheel=0


            print('assign parent objects')
            #Union block的横竖面找parent

            for b in blocks:
                #joinBin=[]
                bpo=self.getObjectByGuid(b)
                #print('bpo='+shortGuid(bpo.guid))
                srfs=rs.ExplodePolysurfaces(b,False)
                for vsrf in vertSrfs:
                    pts2=rs.SurfaceEditPoints(vsrf)
                    for s in srfs:
                        pts1=rs.SurfaceEditPoints(s)
                        if listsEqual(pts1,pts2): #or pts1==pts2r:
                            parentDic[vsrf]=bpo
                rs.DeleteObjects(srfs)

            print(parentDic)

            print('split irregular polygons')
            for s in vertSrfs:
                parent=parentDic[s]
                if parent is None:
                    print('parent is None')
                    rs.SelectObject(s)
                    continue
                #rs.EnableRedraw(True)
                phaseIndex='MASSING'
                typeIndex=parent.typeIndices[0]
                boundary=rs.DuplicateSurfaceBorder(s)
                pts=rs.CurveEditPoints(boundary)
                if len(pts)>5:
                    #print('splitting polygon')
                    #rs.EnableRedraw(False)
                    srfs=splitIrregularPolygon(s)
                    #print('splitIregPoly srfs=',srfs)
                    if srfs is None:
                        continue
                    splitedSrfs+=srfs
                    for ss in srfs:
                        #print(shortGuid(parent.guid))
                        o=self.addObject(ss,phaseIndex,typeIndex,parent)
                        if o is None: continue
                        self.setObjectType(o,typeIndex)
                    #rs.EnableRedraw(True)
                else:
                    splitedSrfs.append(s)
                    o=None
                    try:
                        o=self.addObject(s,phaseIndex,typeIndex,parent)
                    except Exception as e:
                        print(e,s,phaseIndex,typeIndex,parent)
                    if o is None: continue
                    #print('o=',o)
                    self.setObjectType(o,typeIndex)
                    #self.logDataTree()
                rs.DeleteObject(boundary)
        except:
            PrintException()
            rs.EnableRedraw(True)
        self.resumeInteraction()
        rs.EnableRedraw(True)
            #TODO:give properties to splited srfs base on their belonging blocks
            #splitedSrfs contain the splited srfs
            #TODO:join the srfs that share the same manifold
            # for i in range(0,len(splitedSrfs)):
            #     for j in range(0,len(splitedSrfs)):
            #         if i==j: continue
    def handle_GENBLOCK_combo_updates(self,sender,e):
        # txts=self.form.UI_GENBLOCK.lb_selected_block.Text
        # combo=self.form.UI_GENBLOCK.combo_typeIndex1
        # txts=txts.aplit(' ')
        try:
            if self.selectedObject is None: return

            obj=self.selectedObject
            ui=self.form.UI_GENBLOCK
            obj.typeIndices[0]=ui.combo_typeIndex1.Items[ui.combo_typeIndex1.SelectedIndex].Text
            obj.typeIndices[1]=ui.combo_typeIndex2.Items[ui.combo_typeIndex2.SelectedIndex].Text
            obj.typeIndices[2]=ui.combo_typeTopIndex.Items[ui.combo_typeTopIndex.SelectedIndex].Text
            colorI=int(obj.typeIndices[0])
            colorI=colorI%len(COLOR_SET_01)
            color=COLOR_SET_01[colorI]
            rs.ObjectColor(obj.guid,color)
        except:PrintException()

    #update phase object rhino properties
    def updatePhaseObjectColor(self,obj):

        phase=obj.phase
        index=obj.typeIndex
        colors=PHASE_OBJECT_COLORS[phase]
        colorIndex=index%len(colors)
        color=colors[colorIndex]
        #print('@updateColor:',color,obj.guid)
        rs.ObjectColor(obj.guid,color)
        #TODO:return the color PHASE_OBJECT_COLORS[phase][typeIndex]

    #existing model treatments
    def importSrfTypesFromScene(self):

        data=[]
        # srfs=rs.ObjectsByLayer(get_layer_name('TYPESRF'))
        # for f in srfs:
        #     #rs.SelectObject(f)
        #     #rs.ObjectColor(f,(0,0,1))
        #     po=PhaseObject()
        #     po.guid=f
        #     po.phase='TYPESRF'
        #     po.typeIndex=int(rs.ObjectName(f))
        #     po.strTypeDescription=rs.ObjectName(f)
        #     self.updatePhaseObjectColor(po)
        #     data.append(po)
        # self.data=data
        # return
        objs=rs.ObjectsByLayer(get_layer_name('BLOCK'))
        for o in objs:
            po=PhaseObject()
            po.guid=o
            po.phase='BLOCK'
            name=rs.ObjectName(o)
            typeIndex=0
            try: typeIndex=int(name)
            except:pass
            print(name,typeIndex)
            self.setObjectType(po,typeIndex,0)
            data.append(po)

        self.data=data
    # def fixCurrentModel(self):
    #     #fix srf in current scene
    #     layer=get_layer_name('TYPESRF')
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
