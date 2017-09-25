import Rhino
import rhinoscriptsyntax as rs

import rsTools
reload(rsTools)
from rsTools import *

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

    #assign visible button actions
    form.srf_type_UI.regenAll.Click+=genAllMesh
    form.srf_type_UI.viewSrf.Click+=viewSrf
    form.srf_type_UI.viewMesh.Click+=viewMesh
    loadRhinoEvents()

    handleSrfTypeBts1(form,engine)
    handleSrfTypeComboBox(form,engine)

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
def onSelectObjects(sender,e):
    #find selection in current data
    pass

def viewSrf(sender,e):
    print('view srf clicked')
    isolateLayer('genType')
    highlightSelection(ENGINE)
    #self.viewMode_srfType='SRF'
def viewMesh(sender,e):
    print('view mesh clicked')
    isolateLayer('genMesh')
    highlightSelection(ENGINE)

    global ENGINE
    meshes=ENGINE.data.meshType
    if len(meshes)==0:
        genAllMesh()
def genAllMesh(sender=None,e=None):
    global ENGINE
    srfs=ENGINE.data.srfType
    rs.CurrentLayer('genMesh')
    meshes=rs.ObjectsByLayer('genMesh')
    if len(meshes)>0:
        rs.DeleteObjects(meshes)
    ENGINE.data.meshType=[]
    for sAD  in srfs:
        typeI=sAD.srfType
        facadeType=ENGINE.facadeTypes[typeI]
        try:
            m=divideSrfToPattern(sAD.guid,facadeType)
            if rs.IsObject(m):
                mAD=AttrDict()
                mAD.guid=m
                mAD.srfType=typeI
                mAD.srf=sAD.guid
                ENGINE.data.meshType.append(mAD)
        except:
            print('exception in divideSrfToPatter')
            rs.EnableRedraw(True)
        #add mesh to data


def handleSrfTypeBts1(form,engine):
    bts=form.srf_type_UI.bts1
    print(bts)
    class handleBt1():
        def __init__(self,i,engine):
            self.index=i
            self.engine=engine
        def handle(self,sender,e):
            rs.UnselectAllObjects()
            self.engine.clearSelections()
            print('handle bt 1:',self.index)
            selection=[]
            for o in self.engine.data:
                if o.typeIndex==self.index:
                    try:
                        if rs.IsObject(o.guid):
                            selection.append(o)
                    except:
                        print('not guid returned in selection')

            self.engine.setSelection(selection)
            highlightSelection(self.engine)

    for i in range(0,len(bts)):
        bt=bts[i]
        handler=handleBt1(i,engine)
        bt.Click+=handler.handle

def handleSrfTypeComboBox(form,engine):
    combos=form.srf_type_UI.combos
    class handleComboBox():
        def __init__(self,i,engine,combo):
            self.index=i
            self.engine=engine
            self.combo=combo
        def handle(self,sender,e):
            selIndex=self.combo.SelectedIndex
            filename=self.combo.SelectedItem
            print('combo box index changed to ',selIndex)
            engine.updateFacadeType(self.index,filename)
            genMeshType(self.index)

    for i in range(0,len(combos)):
        combo=combos[i]
        handler=handleComboBox(i,engine,combo)
        combo.SelectedIndexChanged+=handler.handle
    #SelectedIndexChanged
    pass
def genMeshType(typeIndex):
    meshes=[]
    srfs=[]
    updatedList=[]
    #remove existing mesh
    for AD in ENGINE.data.meshType:
        if AD.srfType==typeIndex:
            meshes.append(AD.guid)
        else : updatedList.append(AD)
    ENGINE.data.meshType=updatedList
    if len(meshes)>0:
        rs.DeleteObjects(meshes)

    for AD in ENGINE.data.srfType:
        if AD.srfType==typeIndex:
            srfs.append(AD)

    for sAD  in srfs:
        typeI=typeIndex
        facadeType=ENGINE.facadeTypes[typeI]
        print('facade type: ',facadeType)
        try:
            m=divideSrfToPattern(sAD.guid,facadeType)
            if rs.IsObject(m):
                mAD=AttrDict()
                mAD.guid=m
                mAD.srfType=typeI
                mAD.srf=sAD.guid
                ENGINE.data.meshType.append(mAD)
        except:
            print('exception in divideSrfToPatter')
            rs.EnableRedraw(True)
    #generate new mesh


def highlightSelection(engine):
    rs.UnselectAllObjects()
    guids=getGuidFromADs(engine.selectedItems)
    rs.SelectObjects(guids)

def getGuidFromADs(objs):
    guids=[]
    for o in objs:
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
