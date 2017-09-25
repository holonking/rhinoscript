import Rhino
import rhinoscriptsyntax as rs

import rsTools
reload(rsTools)
from rsTools import *

# import Deploy_BaseTypes
# reload(Deploy_BaseTypes)
from Deploy_BaseTypes import *

ENGINE=None
FORM=None

#called by Deploy_App.py
def assignAction(form,engine):
    #engine.importSrfTypesFromScene()
    global ENGINE
    ENGINE=engine
    global FORM
    FORM=form
    form.Closing +=onFormCloseEvents

    #assign GENTYPESRF button actions
    form.UI_GENTYPESRF.bt_regen.Click+=genAllTypeMesh
    form.UI_GENTYPESRF.bt_view_srf.Click+=viewSrf
    form.UI_GENTYPESRF.bt_view_mesh.Click+=viewMesh
    form.UI_GENTYPESRF.bt_inspect.Click+=handle_inspect
    loadRhinoEvents()

    handle_GENTYPESRF_bts1(form,engine)
    handle_GENTYPESRF_bts2(form,engine)
    handle_GENTYPESRF_comboBox(form,engine)

def loadRhinoEvents():
    Rhino.RhinoDoc.EndSaveDocument+=saveEngineData
    Rhino.RhinoDoc.SelectObjects+=onSelectObjects
def unloadRhinoEvents():
    Rhino.RhinoDoc.EndSaveDocument-=saveEngineData
    Rhino.RhinoDoc.SelectObjects-=onSelectObjects
def saveEngineData(sender,e):
    ENGINE.save()
def onFormCloseEvents(sender,e):
    ENGINE.save()
    unloadRhinoEvents()
    print('save data and unload Rhino events')
def onSelectObjects(sender,e):
    #find selection in current data
    pass

def viewSrf(sender,e):
    print('view srf clicked')
    isolateLayer('GENTYPESRF')
    highlightSelection(ENGINE)
    #self.viewMode_srfType='SRF'
def viewMesh(sender,e):
    print('view mesh clicked')
    isolateLayer('GENTYPEMESH')
    highlightSelection(ENGINE)

    # global ENGINE
    # if len(meshes)==0:
    #     genAllMesh()
def handle_inspect(sender,e):
    obj=rs.GetObject('sel obj to inspect')
    if obj is None:
        print('nothing selected')
        return
    inspectObject(obj)
def handle_GENTYPESRF_bts1(form,engine):
    bts=form.UI_GENTYPESRF.bts1
    # print(bts)
    class handleBt1():
        def __init__(self,i,engine):
            self.index=i
            self.engine=engine
        def handle(self,sender,e):
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
            highlightSelection(self.engine)

    for i in range(0,len(bts)):
        bt=bts[i]
        handler=handleBt1(i,engine)
        bt.Click+=handler.handle
def handle_GENTYPESRF_bts2(form,engine):
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

                objs=rs.GetObjects('select obj to change type, and press enter')

                #case of mesh view
                for ro in objs:
                    po,upStream=ENGINE.getObjectByGuid(ro)
                    upStream.typeIndex=self.index
                    genTypeMeshObject(upStream)
            except Exception as e: print(e)

    for i in range(0,len(bts)):
        bt=bts[i]
        handler=handleBt2(i,engine)
        bt.Click+=handler.handle
def handle_GENTYPESRF_comboBox(form,engine):
    combos=form.UI_GENTYPESRF.combos
    class handleComboBox():
        def __init__(self,i,engine,combo):
            self.index=i
            self.engine=engine
            self.combo=combo
        def handle(self,sender,arg):
            try:
                selIndex=self.combo.SelectedIndex
                filename=self.combo.Items[selIndex]

                print('combo box index changed to ',selIndex,filename.Text)
                engine.updateFacadeType(self.index,filename.Text)
            except Exception as e:print('before genTypeMesh',e)
            try:
                genTypeMesh(self.index)
            except Exception as e:
                print('@ handle combo change',Exception,':',e)

    for i in range(0,len(combos)):
        combo=combos[i]
        handler=handleComboBox(i,engine,combo)
        combo.SelectedIndexChanged+=handler.handle
    #SelectedIndexChanged
    pass
def deleteObject(obj):
    if obj is None: return None
    print('delete object')
    print('---',obj.guid)
    print('---',obj.phase)
    print('---',obj.typeIndex)
    print('---',obj.upStream)
    if rs.IsObject(obj.guid): rs.DeleteObject(obj.guid)
    upStream=obj.upStream
    inspectObject(upStream.guid)
    try:#delete the object from upStream
        index=upStream.downStream.index(obj)
        if index>=0: del upStream[index]
    except Exception as e:print('!except at deleteOjbect() 1',e)

    try:#delete the object from data
        index=ENGINE.data.index(obj)
        if index>=0: del ENGINE.data[index]
    except Exception as e:print('!except at deleteOjbect() 2',e)
    return upStream
def deleteObjects(phaseIndex,typeIndex=None):
    #deletes a phase object and returns upStream
    upStream=None
    trashGuid=[]
    updatedList=[]
    # print('before delete, ENGINE.data size:',len(ENGINE.data))

    for o in ENGINE.data :
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
    ENGINE.data=updatedList
    if len(trashGuid)>0:
        # print('delteing ',len(trashGuid),' objects')
        # print('..........................')
        rs.DeleteObjects(trashGuid)
    return upStream
def addObject(guid,phaseIndex,typeIndex,upStream,description='',needUpdate=False):
    o=PhaseObject()
    o.guid=guid
    o.phase=phaseIndex
    o.typeIndex=typeIndex
    o.upStream=upStream
    o.description=description
    o.needUpdate=needUpdate
    upStream.downStream.append(o)
    # print('added o:',o.phase,o.typeIndex)
    ENGINE.data.append(o)
def inspectObject(guid):
    for o in ENGINE.data:
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
def genTypeMeshObject(obj):

    facadeType=ENGINE.facadeTypes[obj.typeIndex]
    downStream=obj.downStream
    layerName='GENTYPEMESH'
    phaseIndex='TYPEMESH'
    print('!!! downStrem size:',len(downStream))
    print(downStream)
    for ds in downStream:
        deleteObject(ds)
        #pass
    try:
        m=divideSrfToPattern(obj.guid,facadeType)
        if rs.IsObject(m):
            rs.ObjectLayer(m,layerName)
            addObject(m,phaseIndex,obj.typeIndex,obj)
    except Exception as e:
        print('exception in divideSrfToPattern:',Exception,':',e)
        rs.EnableRedraw(True)
    pass
def genTypeMesh(typeIndex=None):
    #if not typeIndex given, will regenerate all types
    meshes=[]
    srfs=[]
    updatedList=[]
    phaseIndex='TYPEMESH'
    upStreamIndex='TYPESRF'
    layerName='GENTYPEMESH'
    #remove existing mesh
    try:
        deleteObjects(phaseIndex,typeIndex)
    except Exception as e:print('except at delete :',e)

    #find all the TYPESRF
    try:
        srfs=ENGINE.getObject(upStreamIndex,typeIndex)
    except Exception as e: print('except genTypeMesh->ENGINE.getObject:',e)
    for o  in srfs:
        if typeIndex is not None:
            if not o.typeIndex==typeIndex: continue

        #typeI=typeIndex%len(ENGINE.facadeTypes)
        typeI=o.typeIndex
        #print('typeI:',typeI,ENGINE.facadeTypes)
        try:
            facadeType=ENGINE.facadeTypes[typeI]
            #print('facade type: ',facadeType)
        except Exception as e:
            print('exception in getting ENGINE.facadeTypes',e)
            return
        try:
            m=divideSrfToPattern(o.guid,facadeType)
            if rs.IsObject(m):
                rs.ObjectLayer(m,layerName)
                addObject(m,phaseIndex,typeI,o)
        except Exception as e:
            print('exception in divideSrfToPattern:',Exception,':',e)
            rs.EnableRedraw(True)
    #generate new mesh
def genAllTypeMesh(sender,e):
    genTypeMesh()
def highlightSelection(engine):
    rs.UnselectAllObjects()
    guids=getGuidFromADs(engine.selectedItems)
    rs.SelectObjects(guids)
def getGuidFromADs(oAD):
    guids=[]
    for o in oAD:
        guids.append(o.guid)
    return guids
def isolateLayer(layerName):
    names=rs.LayerNames()
    rs.CurrentLayer('Default')
    for n in names:
        if n=='Default':continue
        if n==layerName:
            layers=rs.LayerVisible(layerName,True)
        else:rs.LayerVisible(n,False)
