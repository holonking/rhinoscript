# -*- coding: utf-8 -*-
import clr
clr.AddReference("RhinoCommon")
import Rhino
import cPickle as pkl
import rhinoscriptsyntax as rs

import RsTools as rt
reload(rt)

import Deploy_BaseTypes

reload(Deploy_BaseTypes)
from Deploy_BaseTypes import *

VIEWMODE = None
import os

# check which OS system, if nt, means windows
if os.name == 'nt':
    PATH_PATTERN = 'C:\\Users\\seah\\Scripting\\rhinoscript\\FacadePatterns\\'
else:
    PATH_PATTERN = './FacadePatterns/'

PHASES = ['BLOCK', 'MASSING', 'MASSINGSRF', 'TYPESRF', 'TYPEMESH', 'COMPONENTS']


def get_layer_name(phase):
    return '$AGL_' + phase


COLOR_SET_01 = [(60, 160, 208),
                (255, 89, 25),
                (242, 192, 120),
                (250, 237, 202),
                (193, 219, 179),
                (126, 188, 137),
                (8, 111, 161)
                ]
COLOR_SET_02 = [(0, 102, 204),
                (51, 153, 255),
                (153, 204, 255),
                (255, 204, 204),
                (255, 102, 102),
                (153, 0, 0)
                ]
DEFAULT_COLOR = (60, 160, 208)
PHASE_OBJECT_COLORS = {
    'BLOCK': [DEFAULT_COLOR],
    'MASSING': [DEFAULT_COLOR],
    'TYPESRF': [DEFAULT_COLOR],
    'TYPESRF': [DEFAULT_COLOR],
    'TYPEMESH': [DEFAULT_COLOR]
}
PHASE_OBJECT_COLORS['BLOCK'] = COLOR_SET_01
PHASE_OBJECT_COLORS['TYPESRF'] = COLOR_SET_01
PHASE_OBJECT_COLORS['TYPEMESH'] = COLOR_SET_02


class Engine():
    def __init__(self):

        # propagate required layers
        for phase in PHASES:
            lay = get_layer_name(phase)
            if not rs.IsLayer(lay): rs.AddLayer(lay)

        # load data
        # self.data=self.loadData()
        self.data = PhaseObject(phase='Root')
        self.importObjectsFromScene()

        # print('imported data:',self.data)
        # print('imported data:')
        # for o in self.data:
        #    print(o.guid)

        # load facade types
        self.loadFacadeTypes()
        # print('loaded facade types:',self.facadeTypes)

        # loggin panel passed from UI
        self.log_panel = None  # still in use?
        self.log_tree_panel = None

        # selection
        self.selectedObjects = []
        self.selectedObject = None
        self.selectedRhiObjects = []
        self.selectedRhiObject = None
        # layers
        self.initLayers()

        # interaction modes
        self.interaction_mode = AttrDict()
        self.interaction_mode.auto_block = True

        self.model_invalidated = False

    def suspendInteraction(self):
        self.interaction_mode.auto_block = False

    def resumeInteraction(self):
        self.interaction_mode.auto_block = True

    def logDataTree(self):
        # if len(self.data)==0:return
        # txt='DATA SIZE:'+str(len(self.data))+'\n'
        txt = ''
        txt += self.data.tree()
        # for po in self.data:
        #     if po.is_root():
        #         txt+=po.tree()
        self.logToTreePanel(txt)

    def logToTreePanel(self, txt):
        try:
            if self.log_tree_panel is None:
                print('engine.log_panel not set')
                return
            else:
                self.log_tree_panel.Text = txt
        except:
            print('engine.log_tree_panel is not yet created')

    def logToObjPanel(self, txt):
        if self.log_obj_panel is None:
            print('engine.log_obj_panel not set')
            return
        else:
            self.log_obj_panel.Text = txt

    def logToRhiPanel(self, txt):
        if self.log_rhi_panel is None:
            print('engine.log_panel not set')
            return
        else:
            self.log_rhi_panel.Text = txt

    # save and load data
    def load(self):
        self.data = self.loadData()

    def loadData(self):
        # serialize the dic from a txt file
        try:
            with open('Data', 'rb') as fp:
                d1 = pkl.load(fp)
            return d1
        except:
            return None

    def save(self):
        self.saveData(self.data)

    def saveData(self, data):
        try:
            filename = 'Data'
            with open(filename, 'wb') as fp:
                pkl.dump(data, fp)
            print('engine data saved sucess')
        except:
            print('save faile failed')

    # object life cycle managements


    def addObject(self, guid, phase, typeIndex,
                  parent=None,
                  description='',
                  needUpdate=False):
        # print('add object ',short_guid(guid))
        if parent is None:
            parent = self.data
        if self.data.find('guid', guid):
            print('obj exists in data')
            return None

        o = PhaseObject()
        o.guid = guid
        o.phase = phase
        o.typeIndex = int(typeIndex)
        o.set_parent(parent)
        o.description = description
        o.needUpdate = needUpdate
        # parent.add_child(o)
        # rhino layer and attributes
        rs.ObjectColor(guid, self.get_color(phase, typeIndex))
        try:
            layer = get_layer_name(phase)
            # print(layer)
            rs.ObjectLayer(guid, layer)
        except Exception as e:
            print(e)
        # layer=self.get_layer_name(phase)
        # rs.ObjectLayer(guid,layer)

        self.logDataTree()
        return o

    def deleteObjectsByGuid(self, guids):
        # print('deleteObjectsByGuid')
        # otd=[]
        if guids is None: return
        for guid in guids:
            o = self.data.find('guid', guid)
            if o is not None:
                o.delete()
        self.logDataTree()

    def deleteObjectByGuid(self, guid):
        o = self.data.find('guid', guid)
        if o is not None:
            o.delete()
        self.logDataTree()

    def deleteObject(self, obj):
        if obj is None: return None
        # if rs.IsObject(obj.guid): rs.DeleteObject(obj.guid)
        obj.delete()

    def deleteObjects(self, phase, typeIndex=None):
        # deletes objects off the same phase and type index
        # <to be confirmed>
        cons = [('phase', phase), ('typeIndex', typeIndex)]
        fos = self.data.find_all(cons)
        for o in fos:
            o.delete()

    # selection management
    def clearSelections(self):
        self.selectedObjects = []

    def addToSelection(self, items):
        for i in items:
            self.selectedObjects.append(i)

    def setSelection(self, items):
        self.selectedObjects = items

    def highlightSelection(self):
        rs.UnselectAllObjects()
        guids = []
        for o in self.selectedObjects:
            if o.guid is not None:
                guids.append(o.guid)
        rs.SelectObjects(guids)

    # data query and inspections
    def inspectObject(self, guid):
        try:
            txt = ''
            for o in self.data.flattern():
                if o.guid == guid:
                    txt += 'guid :' + rt.short_guid(o.guid) + '\n'
                    txt += 'phase:' + str(o.phase) + '\n'
                    txt += 'typeI:' + str(o.typeIndex) + '\n'
                    txt += 'typeIS:['
                    for i in o.typeIndices:
                        txt += str(i) + ','
                    txt += ']\n'
                    if o.parent is not None:
                        txt += 'upStm:' + rt.short_guid(o.parent.guid) + '\n'
                    else:
                        txt += 'upStm:' + 'None\n'
                    txt += 'dnStm:'
                    for c in o.children:
                        txt += rt.short_guid(c.guid) + ' '
                    txt += '\n'
                    txt += 'dsrpt:' + o.description + '\n'
                    # txt+='down stream objects:\n'
                    # for o in o.children:
                    #    txt+=short_guid(o.guid)+'\n'
                    break
            # print(txt)
            return txt
        except:
            PrintException()
            # def getObjectPhaseObject(self,obj,phase):
            # finds the object's up or down stream objects
            # phase1 = obj.phase
            # phase2 = phase
            # i1 = PHASES.index(phase1)
            # i2 = PHASES.index(phase2)
            # direction = self.streamDirection(phase1, phase2)
            # selection = []
            # if direction == 0:
            #     return obj
            # # stop=i2+direction
            # while not i1 == i2:
            #     i1 += direction
            #     selection += obj.children
            # return selection

    def streamDirection(self, phase1, phase2):
        # determin the direction of phase 2 compares to phase 1
        # -1=upStream, 1=downStream, 0=same phase
        if phase1 == phase2: return 0
        i1 = PHASES.index(phase1)
        i2 = PHASES.index(phase2)
        if i2 < i1:
            return -1
        else:
            return 1

    def getObjectByGuid(self, guid):
        for o in self.data:
            if o.guid == guid: return o
        return None  # ,o.parent

    def getObject(self, phaseIndex, typeIndex=None):
        selection = []
        for o in self.data:
            # print('@getObject',o.phase,phaseIndex)
            if o.phase == phaseIndex:
                if typeIndex is None:
                    flag = True
                elif typeIndex == o.typeIndex:
                    flag = True
                else:
                    flag = False
                if flag:
                    selection.append(o)
        return selection

    def setObjectType(self, obj, typeIndex=0, index=None):
        colorI = int(typeIndex) % len(COLOR_SET_01)
        color = COLOR_SET_01[colorI]
        rs.ObjectColor(obj.guid, color)
        if index is None:
            obj.typeIndex = int(typeIndex)
        else:
            obj.typeIndices[int(index)] = typeIndex

    # layer managements
    def initLayers(self):
        # propagate required layers
        parent = get_layer_name('LOCKEDLAYERS')
        rs.AddLayer(get_layer_name('LOCKEDLAYERS'), locked=False)
        for phase in PHASES:
            lay = get_layer_name(phase)
            if not rs.IsLayer(lay):
                rs.AddLayer(lay, locked=False)
            else:
                rs.LayerLocked(lay, False)
                # rs.ParentLayer(lay,parent)
        rs.ExpandLayer(parent, False)

    def isolateLayer(self, layerName):
        names = rs.LayerNames()
        rs.CurrentLayer('Default')
        for n in names:
            if n == 'Default': continue
            if n == get_layer_name('LOCKEDLAYERS'):
                rs.LayerVisible(layerName, True)
                continue
            if n == layerName:
                layers = rs.LayerVisible(layerName, True)
            else:
                rs.LayerVisible(n, False)

    # object generators
    def genTypeMeshObject(self, obj):

        facadeType = self.facadeTypes[obj.typeIndex]
        downStream = obj.children
        layerName = get_layer_name('TYPEMESH')
        phaseIndex = 'TYPEMESH'
        # print('!!! downStrem size:',len(downStream))
        # print(downStream)
        for ds in downStream:
            self.deleteObject(ds)
            # pass
        try:
            m = rt.divide_drf_to_pattern(obj.guid, facadeType)
            if rs.IsObject(m):
                rs.ObjectLayer(m, layerName)
                self.addObject(m, phaseIndex, obj.typeIndex, obj)
        except Exception as e:
            # print('exception in divideSrfToPattern:',Exception,':',e)
            PrintException()
            rs.EnableRedraw(True)
        pass

    def genTypeMesh(self, typeIndex=None):
        # if not typeIndex given, will regenerate all types
        print('genTypeMesh')
        rs.EnableRedraw(False)
        meshes = []
        srfs = []
        updatedList = []
        phaseIndex = 'TYPEMESH'
        upStreamIndex = 'TYPESRF'
        layerName = get_layer_name('TYPEMESH')
        # remove existing mesh
        try:
            # delete from data
            cons = [('phase', 'TYPEMESH')]
            selObjs = self.data.find_all(cons, basket=[])
            if selObjs:
                for o in selObjs:
                    o.delete()
            # clean up other artifacts on this layer
            selguid = rs.ObjectsByLayer(layerName)
            rs.DeleteObjects(selguid)

            # find all the TYPESRF
            # srfs=self.getObject(upStreamIndex,typeIndex)
            cons = [('phase', 'TYPESRF')]
            selObjs = self.data.find_all(cons, basket=[])
            print('{} objects selected'.format(len(selObjs)))
            for o in selObjs:
                if typeIndex is not None:
                    if o.typeIndex != typeIndex:
                        continue
                elif o.typeIndex is None:
                    continue
                else:
                    typeI = o.typeIndex
                    facadeType = self.facadeTypes[typeI]

                    m = rt.divide_drf_to_pattern(o.guid, facadeType)
                    if rs.IsObject(m):
                        rs.ObjectLayer(m, layerName)
                        self.addObject(m, phaseIndex, typeI, o)
        except Exception as e:
            _Print_Exception()
            print(e)
            rs.EnableRedraw(True)
        rs.EnableRedraw(True)

    # checked "self."
    # library and static variables managements
    def loadFacadeTypes(self):
        facadeTypes = []
        import os
        # directory='./FacadePatterns/'
        # directory='C:\\rhinoscript\\gitProject\\FacadePatterns\\'
        directory = self.getPathPattern()
        print(directory)
        files = os.listdir(directory)
        for f in files:
            if f.find('.facade') > 0:
                filename = directory + f
                print(filename)
                # for mac use 'rb'
                # with open(filename,'rb') as fp:
                with open(filename, 'r') as fp:
                    # for line in fp:
                    #    print(line)
                    facadeTypes.append(pkl.load(fp))

        self.facadeTypes = facadeTypes

    def updateFacadeType(self, typeIndex, filename):
        directory = PATH_PATTERN
        filename = directory + filename
        # filename='.\\'+filename

        print('file name @ updateFacadeType: ', filename)
        try:
            with open(filename, 'r') as fp:
                facade = pkl.load(fp)
        except:
            PrintException()

        self.facadeTypes[typeIndex] = facade
        for t in self.facadeTypes:
            print(t)

    def get_color_default(self):
        return DEFAULT_COLOR

    def get_color_set1(self, index):
        return COLOR_SET_01[index % len(COLOR_SET_01)]

    def get_color(self, phase='BLOCK', index=0):
        index = int(index)
        colors = PHASE_OBJECT_COLORS[phase]
        index = index % len(colors)
        color = colors[index]
        return color

    def get_colors(self, phase, index):
        colors = PHASE_OBJECT_COLORS['TYPESRF']
        index = index % len(colors)
        return colors[index]

    def getPathPattern(self):
        return PATH_PATTERN

    # assign UI actions
    def loadRhinoEvents(self):
        print('loading rhino events')
        Rhino.RhinoDoc.EndSaveDocument += self.saveEngineData
        Rhino.RhinoDoc.SelectObjects += self.onSelectObjects
        Rhino.RhinoDoc.AddRhinoObject += self.onAddRhinoObject
        Rhino.RhinoDoc.DeleteRhinoObject += self.onDeleteRhinoObject

    def unloadRhinoEvents(self):
        Rhino.RhinoDoc.EndSaveDocument -= self.saveEngineData
        Rhino.RhinoDoc.SelectObjects -= self.onSelectObjects
        Rhino.RhinoDoc.AddRhinoObject -= self.onAddRhinoObject
        Rhino.RhinoDoc.DeleteRhinoObject -= self.onDeleteRhinoObject

    def saveEngineData(self, sender, e):
        self.save()

    def onDeleteRhinoObject(self, sender, e):
        # do not impliment
        # it will be called even when moving an object
        # if you want to delete an object, please use the UI delete button
        pass

    def onAddRhinoObject(self, sender, e):
        if self.interaction_mode.auto_block:
            obj = rs.FirstObject()
            isBrep = rs.IsBrep(obj)
            if isBrep:
                self.createBlockFromSceneObject(obj)
                self.data.invalidate()

    def onFormCloseEvents(self, sender, e):
        self.save()
        self.unloadRhinoEvents()
        print('save data and unload Rhino events')

    def onSelectObjects(self, sender, e):
        try:
            sel = rs.SelectedObjects()
            self.selectedRhiObjects = sel
            txt = 'sel ' + str(len(sel)) + ':'

            for o in sel:
                txt += rt.short_guid(o) + ','
            # print(txt)
            self.logToRhiPanel(txt)
            if len(sel) == 0:
                self.selectedRhiObject = None
                self.selectedObject = None
                self.form.UI_GENBLOCK.lb_selected_block.Text = 'Select block to edit'
            if len(sel) == 1:
                guid = sel[0]
                self.selectedRhiObject = guid
                txt = self.inspectObject(guid)
                self.logToObjPanel(txt)
                # obj=self.getObjectByGuid(guid)
                obj = None
                for po in self.data.flattern():
                    if po.guid == guid:
                        obj = po
                        po.is_selected = True
                    else:
                        po.is_selected = False
                if obj is not None:
                    self.selectedObject = obj
                    # try to update the block panel
                    if obj.phase == 'BLOCK':
                        self.update_GENBLOCK_PROPS()
                self.logDataTree()
        except:
            PrintException()
            # find selection in current data

    def setComboIndexfromItem(self, combo, item):
        index = 0
        # print(combo,item)
        index = 0
        try:
            index = combo.Items.index(item)
        except:
            pass
        # combo.SelectedIndex=index
        combo.Text = str(item)

    def update_GENBLOCK_PROPS(self):
        try:
            clear = False
            if self.selectedObject is None:
                clear = True
            elif self.selectedObject.phase != 'BLOCK':
                clear = True
            if clear:
                self.form.UI_GENBLOCK.lb_selected_block.Text = 'Select Block to edit'
                self.form.UI_GENBLOCK.combo_typeIndex1.SelectedIndex = 0
                self.form.UI_GENBLOCK.combo_typeIndex2.SelectedIndex = 0
                self.form.UI_GENBLOCK.combo_typeTopIndex.SelectedIndex = 0
            else:
                obj = self.selectedObject
                self.form.UI_GENBLOCK.lb_selected_block.Text = 'Editing ' + rt.short_guid(obj.guid)
                self.setComboIndexfromItem(self.form.UI_GENBLOCK.combo_typeIndex1, obj.typeIndices[0])
                self.setComboIndexfromItem(self.form.UI_GENBLOCK.combo_typeIndex2, obj.typeIndices[1])
                self.setComboIndexfromItem(self.form.UI_GENBLOCK.combo_typeTopIndex, obj.typeIndices[2])
        except:
            PrintException()

    def assignAction(self, form):

        # engine.importSrfTypesFromScene()

        self.form = form
        form.Closing += self.onFormCloseEvents

        # assign tabcontrol page change events
        form.tabControl.SelectedIndexChanged += self.handle_tab_change

        # assign GENBLOCK button actions
        # form.UI_GENBLOCK.bt_view_block.Click+=self.handle_GENBLOCK_bt_view_block
        # form.UI_GENBLOCK.bt_view_srf.Click+=self.handle_GENBLOCK_bt_view_srf
        form.UI_GENBLOCK.bt_interact.Click += self.handle_GENBLOCK_bt_interact
        form.UI_GENBLOCK.combo_typeIndex1.SelectedIndexChanged += self.handle_GENBLOCK_combo_updates
        form.UI_GENBLOCK.combo_typeIndex2.SelectedIndexChanged += self.handle_GENBLOCK_combo_updates
        form.UI_GENBLOCK.combo_typeTopIndex.SelectedIndexChanged += self.handle_GENBLOCK_combo_updates

        # assign GENTYPESRF button actions
        form.UI_GENTYPESRF.bt_regen.Click += self.handle_regen
        form.UI_GENTYPESRF.bt_view_srf.Click += self.handle_GENTYPESRF_bt_viewSrf
        form.UI_GENTYPESRF.bt_view_mesh.Click += self.handle_GENTYPESRF_bt_viewMesh
        form.UI_GENTYPESRF.bt_inspect.Click += self.handle_GENTYPESRF_bt_inspect

        self.loadRhinoEvents()

        self.handle_GENTYPESRF_bts1()
        self.handle_GENTYPESRF_bts2()
        self.handle_GENTYPESRF_comboBox()

        self.log_tree_panel = form.treeTextBox
        self.log_obj_panel = form.objTextBox
        self.log_rhi_panel = form.rhiTextBox

        # TOOBAR action assignment
        form.UI_TOOLBAR.bt_delete.Click += self.handle_TOOLBAR_bt_delete

        self.logDataTree()

    def handle_regen(self, sender, e):
        self.genTypeMesh()

    def handle_tab_change(self, sender, e):
        index = sender.SelectedIndex
        if index == 0:
            self.handle_tab_BLOCK()
        elif index == 1:
            self.handle_tab_TYPESRF()
        elif index == 2:
            self.handle_tab_MESH()

    def handle_TOOLBAR_bt_delete(self, sender, e):
        print('del pressed')
        if self.selectedObject:
            print('deleting:', self.selectedObject.to_string())
            self.selectedObject.delete()
        self.logDataTree()

    def handle_GENTYPESRF_bt_viewSrf(self, sender, e):
        print('view srf clicked')
        global VIEWMODE
        VIEWMODE = 'TYPESRF'
        self.isolateLayer(get_layer_name('TYPESRF'))
        self.highlightSelection()
        # self.viewMode_srfType='SRF'

    def handle_GENBLOCK_bt_interact(self, sender, e):
        try:
            if self.interaction_mode.auto_block:
                self.form.UI_GENBLOCK.bt_interact.Text = '-Intr'
                self.interaction_mode.auto_block = False
            else:
                self.form.UI_GENBLOCK.bt_interact.Text = '+Intr'
                self.interaction_mode.auto_block = True
        except:
            PrintException()

    def handle_GENTYPESRF_bt_viewMesh(self, sender, e):
        print('view mesh clicked')
        global VIEWMODE
        VIEWMODE = 'TYPESRF'
        self.isolateLayer(get_layer_name('TYPEMESH'))
        self.highlightSelection()

    def handle_GENTYPESRF_bt_inspect(self, sender, e):
        obj = rs.GetObject('sel obj to inspect')
        if obj is None:
            print('nothing selected')
            return
        self.inspectObject(obj)

    def handle_GENTYPESRF_bts1(self):
        form = self.form
        bts = form.UI_GENTYPESRF.bts1

        # print(bts)
        class handleBt1():
            def __init__(self, i, engine):
                self.index = i
                self.engine = engine
                self.toggle = False

            def handle(self, sender, e):
                try:
                    if not self.toggle:
                        self.toggle = True
                        rs.UnselectAllObjects()
                        self.engine.clearSelections()
                        selection = []

                        # print('handle bt 1:',self.index)
                        # impliment:
                        # select all objects with given typeIndex
                        print(self.index)
                        cons = [('typeIndex', self.index)]
                        sel_objs = self.engine.data.find_all(cons, basket=[])
                        self.engine.setSelection(sel_objs)
                        self.engine.highlightSelection()
                    else:
                        self.toggle = False
                        self.engine.setSelection([])
                        rs.UnselectAllObjects()
                except Exception as e:
                    print(e)
                    _Print_Exception()

        from Eto.Drawing import Color
        for i in range(0, len(bts)):
            bt = bts[i]
            handler = handleBt1(i, self)
            bt.Click += handler.handle

    def handle_GENTYPESRF_bts2(self):
        form = self.form
        # handle the second button which sets srf to a type
        bts = form.UI_GENTYPESRF.bts2

        # print(bts)
        class handleBt2():
            def __init__(self, i, engine):
                self.index = i
                self.engine = engine

            def handle(self, sender, e):
                try:
                    rs.UnselectAllObjects()
                    self.engine.clearSelections()

                    objs = rs.SelectedObjects()
                    if len(objs) == 0:
                        objs = rs.GetObjects('select obj to change type, and press enter')

                    # case of mesh view
                    for ro in objs:
                        po, upStream = self.engine.getObjectByGuid(ro)
                        upStream.typeIndex = self.index
                        rs.ObjectColor(upStream.guid, SRFTYPECOLORS[self.index])
                        # TODO:the following line deleted upstream from engine
                        # TODO:color is not updating
                        # self.engine.genTypeMeshObject(upStream)
                except Exception as e:
                    print(e)

        for i in range(0, len(bts)):
            bt = bts[i]
            handler = handleBt2(i, self)
            bt.Click += handler.handle

    def handle_GENTYPESRF_comboBox(self):
        form = self.form
        combos = form.UI_GENTYPESRF.combos

        class handleComboBox():
            def __init__(self, i, engine, combo):
                self.index = i
                self.combo = combo
                self.engine = engine

            def handle(self, sender, arg):
                try:
                    selIndex = self.combo.SelectedIndex
                    filename = self.combo.Items[selIndex]

                    print('combo box index changed to ', selIndex, filename.Text)
                    self.engine.updateFacadeType(self.index, filename.Text)
                except Exception:
                    PrintException()
                try:
                    self.engine.genTypeMesh(self.index)
                except Exception as e:
                    print('@ handle combo change', Exception, ':', e)

        for i in range(0, len(combos)):
            combo = combos[i]
            handler = handleComboBox(i, self, combo)
            combo.SelectedIndexChanged += handler.handle
            # SelectedIndexChanged

    def handle_tab_BLOCK(self):
        self.isolateLayer(get_layer_name('BLOCK'))

    def handle_tab_TYPESRF(self):
        self.suspendInteraction()
        rs.EnableRedraw(False)
        try:
            # only display TYPESRF layer
            # this session union and split blocks into TYPESRF
            phaseIndex = 'TYPESRF'
            layername = get_layer_name(phaseIndex)
            tolerance = 0.0001
            self.isolateLayer(layername)

            # delete existing TYPESRF phase objects
            selobjs = self.data.find_all([('phase', phaseIndex)], basket=[])
            for o in selobjs:
                print('sel:' + str(o))
                o.delete()
            # delete other trash on this layer
            # incase created intentionally or
            # by products which did not assign a parent
            trash = rs.ObjectsByLayer(layername)
            rs.DeleteObjects(trash)

            rs.CurrentLayer(layername)

            cons = [('phase', 'BLOCK')]
            obj_blocks = self.data.find_all(cons)
            rhi_blocks = self.data.find_all_guids(cons)
            # Rhino operations:
            # copy the rhino blocks
            cblocks = rs.CopyObjects(rhi_blocks)
            # apply union operation
            ublocks = rs.BooleanUnion(cblocks, True)

            splitedSrfs = []
            horzSrfs = []
            vertSrfs = []

            # 找出union block里的横竖面
            # print('Sparate horz and vert srfs')
            if ublocks is None:
                ublocks = cblocks

            for b in ublocks:
                os = rs.ExplodePolysurfaces(b, True)
                print('os', os)
                # 先把水平面分走
                horzSrfs = []
                vertSrfs = []

                for s in os:
                    if s is None:
                        continue
                    if not rs.IsObject(s):
                        continue
                    isHor, direct = rt.isHorizonalSrf(s, True)
                    if rt.isHorizonalSrf(s):
                        if direct < 0:  # horizontal facing down
                            rs.ObjectColor(s, (255, 0, 0))
                        else:  # horizontal facing up
                            rs.ObjectColor(s, COLOR_SET_01[5])
                        horzSrfs.append(s)
                    else:
                        vertSrfs.append(s)

            # got all horizontal srfs in horzSrfs
            # got all vertical srfs in vertSrfs
            # now find all parents for each vertSrfs by comparison
            blockedSrf = []
            # parentDict associates each vertical srf #to a block phase object
            # parentDict['vertSrf]=block phase object
            parentDic = {}
            orphans = []  # a collection for guid of objects who do not match any parents
            wheel = 0

            print('assign parent objects')
            # Union block的横竖面找parent
            print('obj_blocks len={}'.format(len(obj_blocks)))
            for po in obj_blocks:
                srfs = rs.ExplodePolysurfaces(po.guid, False)
                for i in range(len(vertSrfs)):
                    vsrf = vertSrfs[i]
                    pts2 = rs.SurfaceEditPoints(vsrf)
                    is_orphan = True
                    for s in srfs:
                        pts1 = rs.SurfaceEditPoints(s)
                        if rt.lists_equal(pts1, pts2):
                            parentDic[vsrf] = po
                            is_orphan = False
                            # del vertSrfs[i]
                            # i-=1
                            break
                    if is_orphan:
                        # select the srfs who can not match a parent
                        orphans.append(vsrf)
                rs.DeleteObjects(srfs)
            # finish iterating one block object

            # print(parentDic)
            print('split irregular polygons')
            for s in vertSrfs:
                if not s in parentDic.keys():
                    print('parent is None')
                    rs.SelectObject(s)
                    continue
                parent = parentDic[s]
                if parent is None:
                    print('819 parent got from parent dict is None')
                    rs.SelectObject(s)
                    continue
                # rs.EnableRedraw(True)
                phaseIndex = 'TYPESRF'
                typeIndex = parent.typeIndices[0]
                boundary = rs.DuplicateSurfaceBorder(s)
                pts = rs.CurveEditPoints(boundary)
                # if False:
                if len(pts) > 5:
                    # print('splitting polygon')
                    # rs.EnableRedraw(False)
                    srfs = rt.splitIrregularPolygon(s)
                    # print('splitIregPoly srfs=',srfs)
                    if srfs is None:
                        continue
                    splitedSrfs += srfs
                    for ss in srfs:
                        # print(short_guid(parent.guid))
                        print('split srf:', ss)
                        print('phaseIndex:', phaseIndex)
                        print('typeIndex:', typeIndex)
                        print('parent:', parent)
                        o = self.addObject(ss, phaseIndex, typeIndex, parent)
                        if o is None: continue
                        self.setObjectType(o, typeIndex)
                        # rs.EnableRedraw(True)
                else:
                    splitedSrfs.append(s)
                    print('parent=', parent)
                    print('type=', typeIndex)
                    print('s=', s)
                    print('phase=', phaseIndex)

                    o = self.addObject(guid=s, phase=phaseIndex,
                                       typeIndex=typeIndex, parent=parent)
                    if o is None:
                        continue
                        # self.setObjectType(o,typeIndex)
                rs.DeleteObject(boundary)
        # //////////////////////////////////////////////
        # //// now got all slited surfaces as TYPESRF
        # //////////////////////////////////////////////

        except Exception as e:
            print('850 exception:', e)
            _Print_Exception()
            # PrintException()
            rs.EnableRedraw(True)
        self.resumeInteraction()
        rs.EnableRedraw(True)
        # TODO:give properties to splited srfs base on their belonging blocks
        # splitedSrfs contain the splited srfs
        # TODO:join the srfs that share the same manifold
        # for i in range(0,len(splitedSrfs)):
        #     for j in range(0,len(splitedSrfs)):
        #         if i==j: continue

    def handle_tab_MESH(self):
        print('view mesh clicked')
        global VIEWMODE
        VIEWMODE = 'TYPEMESH'
        self.isolateLayer(get_layer_name('TYPEMESH'))
        # self.highlightSelection()
        self.genTypeMesh()

    def handle_GENBLOCK_combo_updates(self, sender, e):
        # txts=self.form.UI_GENBLOCK.lb_selected_block.Text
        # combo=self.form.UI_GENBLOCK.combo_typeIndex1
        # txts=txts.aplit(' ')
        try:
            if self.selectedObject is None: return

            obj = self.selectedObject
            ui = self.form.UI_GENBLOCK

            obj.typeIndices[0] = ui.combo_typeIndex1.Items[ui.combo_typeIndex1.SelectedIndex].Text
            obj.typeIndices[1] = ui.combo_typeIndex2.Items[ui.combo_typeIndex2.SelectedIndex].Text
            obj.typeIndices[2] = ui.combo_typeTopIndex.Items[ui.combo_typeTopIndex.SelectedIndex].Text
            obj.typeIndex = obj.typeIndices[0]
            colorI = int(obj.typeIndices[0])
            colorI = colorI % len(COLOR_SET_01)
            color = COLOR_SET_01[colorI]
            rs.ObjectColor(obj.guid, color)
            name = '{},{},{},{}'.format(
                obj.typeIndex,
                obj.typeIndices[0],
                obj.typeIndices[0],
                obj.typeIndices[0]
            )
            rs.ObjectName(obj.guid, name)
        except:
            PrintException()

    # update phase object rhino properties
    def updatePhaseObjectColor(self, obj):

        phase = obj.phase
        index = obj.typeIndex
        colors = PHASE_OBJECT_COLORS[phase]
        colorIndex = index % len(colors)
        color = colors[colorIndex]
        # print('@updateColor:',color,obj.guid)
        rs.ObjectColor(obj.guid, color)
        # TODO:return the color PHASE_OBJECT_COLORS[phase][typeIndex]

    # existing model treatments
    def createBlockFromSceneObject(self, guid):
        obj = guid
        # isBrep=rs.IsBrep(obj)
        # if self.interaction_mode.auto_block and isBrep:
        name = rs.ObjectName(obj)
        if name is None:
            name = '0'
        if name == '':
            name = '0'
        types = name.split(',')
        o = self.addObject(obj, 'BLOCK', int(types[0]), None)
        if len(types) == 1:
            o.typeIndices[0] = types[0]
        else:
            for i in range(1, len(types)):
                o.typeIndices[i - 1] = types[i]

    def importObjectsFromScene(self):
        objs = rs.ObjectsByLayer(get_layer_name('BLOCK'))
        for o in objs:
            self.createBlockFromSceneObject(o)


def _Print_Exception():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    print ('EXCEPTION IN ({}, LINE {})'.format(filename, lineno))
