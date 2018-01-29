import rhinoscriptsyntax as rs
import Rhino
from Rhino.Geometry import *
import RsTools.FormMorph as rtf
import RsTools.MeshTools as rtm
import RsTools.Colors as rtc
import shape_UI as shapeUI

reload(rtf)
reload(shapeUI)
reload(rtm)
reload(rtc)

CLEAR_ON_RESET = False
GENLAYER = 'SHAPE_GRAMMAR_GENERATED_OBJECTS'
GENHIDDEN = 'SHAPE_GRAMMAR_GENERATED_HIDDEN'
ENABLEDARAW = False
TAKESNAPSHOTS = False
PRINTSTEPS=True
ADDSTEPS=True
COLORIZE=True
COLORONSTEP=True



rs.AddLayer(GENLAYER)
rs.AddLayer(GENHIDDEN)


class Align():
    E=1
    S=2
    W=3
    N=4
    NE=41
    SE=21
    NW=43
    SW=23
    M=5

class Geometry():
    def __init__(self, guid, position=None, vects=None,
                 size=None, rotation=None, name='', parent=None):
        self.guid = guid
        self._name = name
        try:
            rs.ObjectName(self.guid,name)
        except:
            pass
        self.size = Vector3d(size) if size is not None else Vector3d(3, 3, 3)
        self.position = Point3d(position) if position is not None else Point3d(0, 0, 0)
        self.rotate = Vector3d(rotation) if rotation is not None else Vector3d(0, 0, 0)
        self.vects = []
        for v in vects:
            self.vects.append(Vector3d(v))
        self.plane = Plane(self.position, self.vects[0], self.vects[1])
        self._parent = parent
        if parent is not None:
            self.set_parent(parent)
        self.children = []
        self._components=[]
        self._staged=True
        self._visible=True
        self._color=None

    @property
    def name(self):
        return self._name
    @name.setter
    def name(self,value):
        self._name=value
        ENGINE.add_name(value)
        try:
            rs.ObjectName(self.guid,value)
        except:
            pass

    @property
    def color(self):
        return self._color
    @color.setter
    def color(self,value):
        self._color=value
        self._set_color(value)

    def __str__(self):
        return '{}'.format(self.name)
        #return '{}<vects:({},{})>'.format(self.name, _str_vects(self.vects), list(self.size))
        # return '{}<pos:({}),size:{},vectsu:({}),id:{}>'.format(
        #    self.name, self.position,self.size,self.vects[0],self.guid)

    def _set_color(self,color):
        try:
            rs.ObjectColor(self.guid,color)
        except:
            pass

    def move(self,transform):
        offset = Point3d(transform[0],transform[1],transform[2])
        #print('offset:',str(offset))
        self.position += offset
        rs.MoveObject(self.guid, offset)

    def print_tree(self, level=0):
        prefix = '        ' * level
        print(prefix + str(self))
        for c in self.children:
            c.print_tree(level + 1)

    def format_tree(self, level=0, init_str=''):
        prefix = '        ' * level
        init_str += prefix + str(self)
        for c in self.children:
            c.print_tree( level+1 )

    @property
    def root(self):
        if self._parent is None:
            return self
        return self._parent.root

    def set_parent(self, parent):
        self._parent = parent
        self._parent.children.append(self)

    def get_shape(self, guid):
        # override
        pass

    def get_vect(self, direction, unitized=True):
        if unitized:
            return self.vects[direction]
        else:
            return self.vects[direction] * self.size[direction]

    def invert(self,direction='x',copy=True):
        if direction=='y':
            sp=self.position
            ep=self.position + self.vects[0]
            offset=self.vects[1]*self.size[1]
        elif direction=='x':
            sp = self.position
            ep = self.position + self.vects[1]
            offset = self.vects[0] * self.size[0]

        mirrored=rs.MirrorObject(self.guid,sp,ep,copy)
        rs.MoveObject(mirrored,offset)
        position = self.position + offset
        vects=[]
        if direction =='x':
            vects.append(Vector3d(self.vects[0] * -1))
            vects.append(Vector3d(self.vects[1]))
            vects.append(Vector3d(self.vects[2]))
        elif direction == 'y':
            vects.append(Vector3d(self.vects[0]))
            vects.append(Vector3d(self.vects[1] * -1))
            vects.append(Vector3d(self.vects[2]))

        size=Vector3d(self.size)


        if copy:
            return Geometry(mirrored,position,vects,size,name=self.name)
            #return #create_box(size, position, vects, self.name)
        else:
            self.guid=mirrored
            self.position = position
            self.vects = vects
            return self





    def unstage(self):
        self._staged=False
        self._visible=False
        self.hide()

    def stage(self):
        self._staged=True


    def hide(self):
        self._visible=False
        rs.HideObject(self.guid)

    def show(self):
        self._visible=True
        rs.ShowObject(self.guid)

    def delete(self):
        self.unstage()
        rs.ShowObject(self.guid)
        rs.DeleteObject(self.guid)

    def select(self):
        rs.SelectObject(self.guid)

    def clone(self,add_to_engine=True):
        guid=rs.CopyObject(self.guid)
        position=Point3d(self.position)
        size=Vector3d(self.size)
        vects=[]
        for i in range(3):
            vects.append(Vector3d(self.vects[i]))
        geo=Geometry(guid,position,vects,size,name=self.name)
        if add_to_engine:
            ENGINE.add(geo)
        return geo

    def extract_face(self, directions=['S']):
        outfaces = []
        try:
            mesh=rs.coercemesh(self.guid)
        except:
            print('geomerty must be a mesh')
            return None
        indice=[]
        if 'S' in directions:
            i=rtm.BOX_FACE_ID.front
            guid = rtm.box_face(mesh, i)
            pos=self.position
            vects=[self.vects[0],self.vects[2],-self.vects[1]]
            size=Vector3d(self.size[0],self.size[2],0)
            face=GeoFace(guid,pos,vects,size)
            outfaces.append(face)
        if 'N' in directions:
            i = rtm.BOX_FACE_ID.back
            guid = rtm.box_face(mesh, i)
            pos = self.position + self.vects[1]*self.size[1] + self.vects[0]*self.size[0]
            vects = [-self.vects[0], self.vects[2], self.vects[1]]
            size = Vector3d(self.size[0], self.size[2],0)
            face = GeoFace(guid, pos, vects, size)
            outfaces.append(face)
        if 'E' in directions:
            i = rtm.BOX_FACE_ID.right
            guid = rtm.box_face(mesh, i)
            pos = self.position + self.vects[0]*self.size[0]
            vects = [self.vects[1], self.vects[2], self.vects[0]]
            size = Vector3d(self.size[1], self.size[2],0)
            face = GeoFace(guid, pos, vects, size)
            outfaces.append(face)
        if 'W' in directions:
            i = rtm.BOX_FACE_ID.left
            guid = rtm.box_face(mesh, i)
            pos = self.position + self.vects[1]*self.size[1]
            vects = [-self.vects[1], self.vects[2], -self.vects[0]]
            size = Vector3d(self.size[1], self.size[2],0)
            face = GeoFace(guid, pos, vects, size)
            outfaces.append(face)
        if 'T' in directions:
            i = rtm.BOX_FACE_ID.top
            guid = rtm.box_face(mesh, i)
            pos = Point3d(self.position)
            vects =self.vects
            size = Vector3d(self.size[1], self.size[2], 0)
            face = GeoFace(guid, pos, vects, size)
            outfaces.append(face)
        if 'B' in directions:
            i = rtm.BOX_FACE_ID.bottom
            guid = rtm.box_face(mesh, i)
            pos = Point3d(self.position)
            vects =self.vects
            size = Vector3d(self.size[1], self.size[2], 0)
            face = GeoFace(guid, pos, vects, size)
            outfaces.append(face)
        return outfaces

class GeoGroup(Geometry):
    def __init__(self, guid, position=None, name='group', parent=None):
        #super(GeoGroup, self).__init__(guid)
        #self.guid=guid
        self.guid = guid
        self.name = name
        #self.size = Vector3d(size) if size is not None else Vector3d(3, 3, 3)
        self.position = Point3d(position) if position is not None else Point3d(0, 0, 0)
        #self.rotate = Vector3d(rotation) if rotation is not None else Vector3d(0, 0, 0)
        #self.vects = []

        self._parent = parent
        if parent is not None:
            self.set_parent(parent)
        self.children = []
        self._components = rs.ObjectsByGroup(guid)
        self._staged = True
        self._visible = True

    def _set_color(self,color):
        for o in self._components:
            o.color=color

    def hide(self):
        self._visible=False
        try:
            rs.HideObjects(self._components)
        except Exception as e:
            print('hide failed:{}'.format(e))

    def show(self):
        self._visible=True
        rs.ShowObjects(self._components)

    def delete(self):
        rs.DeleteObjects(self._components)

    def unstage(self):
        self._staged = False
        self.hide()

    def stage(self):
        self._staged = True
        self.show()

    def hide(self):
        self._visible = False
        rs.HideObjects(self._components)

    def show(self):
        self._visible = True
        rs.ShowObjects(self._components)


    def select(self):
        rs.SelectObjects(self._components)

class GeoFace(Geometry):
    pass

class NameGroup():
    def __init__(self, names, group_name):
        self.names = names
        self.name = group_name

    def get_objects(self):
        basket = []
        for name in self.names:
            objs = ENGINE.get_by_name(name)
            if objs:
                basket += objs
        return basket

    def hide(self):
        objs=[]
        for n in self.names:
            objs+=ENGINE.get_by_name(n)
        for o in objs:
            o.hide()

    def delete(self):
        for n in self.names:
            objs += ENGINE.get_by_name(n)
            for o in objs:
                o.unstage()
                rs.DeleteObject(o.guid)


    def unstage(self):
        objs = []
        for n in self.names:
            objs += ENGINE.get_by_name(n)
            for o in objs:
                o.unstage()


class Engine():
    # system
    def __init__(self):
        self._reset()
        self._create_ui()
        self._enable_redraw=True
        self._path='C:\\Scripting\\rhinoscript\\'


    def _reset(self):
        try:
            self._delete_all()
        except:
            pass
        self.data = []
        self.step = 0
        self.step_texts = []
        self.step_geometry = []
        self.name_list=[]
        self._imported_components = {}
        self.name_color_wheel=rtc.ColorWheel()
        self._attach_rhino_events()
        self._named_colors={}
        self._mapped_components={}
        try:
            print(' hidden count:{}'.format(len(self._hidden_rhino_objects)))
            rs.EnableRedraw(False)
            for i in range(len(self._hidden_rhino_objects)):
                id=self._hidden_rhino_objects.pop()
                rs.ShowObject(id)
            if ENABLEDARAW:
                rs.EnableRedraw(True)
        except Exception as e:
            print(e)
            self._hidden_rhino_objects=[]
        try:
            self.ui.tb_rules.Text = ''
        except:
            print('unable to reset ui text')
            pass

    def _attach_rhino_events(self):
        Rhino.RhinoDoc.SelectObjects += self._onSelectObjects

    def _dettach_rhino_events(self):
        Rhino.RhinoDoc.SelectObjects -= self._onSelectObjects

    def _create_ui(self):
        self.ui=shapeUI.ShapeForm()
        self.ui.rules.slider.callbacks.append(self._slider_value_changed)
        # self.ui.Show()

    def show_ui(self):
        try:
            self.ui.show()
        except:
            self._create_ui()
            self.ui.show()

    def _onSelectObjects(self, sender,e):
        sel = rs.SelectedObjects()
        if sel:
            guid=sel[0]
            if self.ui:
                self.ui.rules.tb_guid.Text=str(guid)
        else:
            if self.ui:
                self.ui.rules.tb_guid.Text='selection empty'

    def _hide_rhino_object(self,id):
        self._hidden_rhino_objects.append(id)
        rs.HideObject(id)

    def _hide_all(self):
        for o in self.data:
            o.hide()

    def _delete_all(self):
        for o in self.data:
                o.delete()

    def unstage_name(self,name):
        objs=ENGINE.get_by_name(name)
        for o in objs:
            o.unstage()

    def _slider_value_changed(self,value):
        #print('_slider_value_changed step:{}'.format(value))
        index=int(value)
        self.ui.rules.tb_rules.Text = self._format_step_text(index+1)
        #following lines are for RulePanel2
        # if len(self.ui.rules.pn_rules.Content.Items)>=value:
        #     try:
        #         self.ui.rules.pn_rules.Content.Items.RemoveAt(value-1)
        #     except:
        #         print('fail to remove')

        if self._enable_redraw:
            rs.EnableRedraw(False)
            self._hide_all()
            rs.ShowObjects(self.step_geometry[index])
            rs.EnableRedraw(True)


    def _snap_shot(self):
        pass

    def set_path(self, path):
        self._path = path

    def select_name(self, name):
        for o in self.data:
            if o.name == name:
                o.select()

    def clear_doc(self):
        self._delete_all()
        self.delete_imported_components()

        rs.CurrentLayer('Default')
        rs.PurgeLayer(GENLAYER)
        rs.AddLayer(GENLAYER)
        rs.CurrentLayer(GENLAYER)

    def delete_imported_components(self):
        for v in self._imported_components.values():
            print('deleting {}'.format(v))
            objs=rs.ObjectsByGroup(v['group'])
            rs.DeleteObjects(objs)
        self._imported_components={}

    def enable_redraw(self,flag=True):
        rs.EnableRedraw(flag)
        self._enable_redraw=flag
        if flag:
            rs.EnableRedraw(False)
            self._hide_all()
            if len(self.step_geometry)>0:
                rs.ShowObjects(self.step_geometry[-1])
            rs.EnableRedraw(True)

    def add_name(self,name):
        if name in self.name_list:
            #print('- {} exist'.format(name))
            return False
        #print('+ {} added'.format(name))

        self.name_list.append(name)
        color=self.name_color_wheel.get_next()
        print(color)
        self._named_colors[name]=color
        # bt=self.ui.names.add_name(name,color)
        #
        # def on_button_press(sender, e):
        #     rs.UnselectAllObjects()
        #     self.select_name(name)
        #
        # bt.Click += on_button_press

        return True

    def add_step(self,text):
        if not ADDSTEPS:
            return
        if PRINTSTEPS:
            print('{} | data count:{}'.format(text,len(self.data)))
        self.step_texts.append(text)
        current_objs=[]
        for o in self.data:
            if isinstance(o,GeoGroup) and o._staged and o._visible:
                objs=o._components
                current_objs += objs
            elif isinstance(o,Geometry) and o._staged and o._visible:
                    current_objs.append(o.guid)
        self.step_geometry.append(current_objs)

        # UI operations

        #following line is for RulePanel2
        #self.ui.rules.add_rule('asd')
        self.ui.rules.slider.Value=self.step
        self.ui.rules.slider.MaxValue=self.step

        self.step+=1

    def add_imported_component(self,name,rhinogroup,w,h):
        self._imported_components[name]={'size':(w,h),'group':rhinogroup}

    def get_imported_component(self,name):
        comp=self._imported_components[name]
        w=comp['size'][0]
        h = comp['size'][1]
        group=comp['group']
        return group,w,h

    def _format_step_text(self,i=None):
        print('step:',i)
        text=''
        length=len(self.step_texts)
        if i is None or i > length:
            i=length
        for j in range(i):
            t=self.step_texts[j]
            text+=t+'\n'
        return text

    def enable_snap_shot(self, flag=True):
        TAKESNAPSHOTS = flag

    def add(self, obj):
        self.data.append(obj)
        self.add_name(obj.name)

    def add_multiple(self, objs):
        self.data += objs

    def unstage_object(self, obj):
        #print('ENGINE.delete start')
        if isinstance(obj,GeoGroup):
            objs=obj._components
            for o in objs:
                o.unstage()
        else:
            obj.unstage()

    def unstage_objects(self, objs):
        #print('ENGINE.delete start')
        for obj in objs:
            if isinstance(obj,GeoGroup):
                objs=obj._components
                for o in objs:
                    o.unstage()
            else:
                obj.unstage()

    def print_data(self):
        for o in self.data:
            print(o)

    def print_tree(self):
        print('-----print tree------')
        for o in self.data:
            if isinstance(o,Geometry) and\
                        o._parent is None and\
                        o._staged:
                o.print_tree()

    def get_by_name(self, name, return_index=False):
        basket = []
        indice = []
        for i in range(len(self.data)):
            o = self.data[i]
            if isinstance(o,Geometry) and o._staged and o.name == name:
                basket.append(o)
                indice.append(i)
        if return_index:
            return basket, indice
        return basket

    def delete_objects(self, objs):
        for o in objs:
            i = self.data.index(o)
            #print('deleting objct:{}, index:{}'.format(o.name,i))
            if i >= 0:
                #del self.data[i]
                o.unstage()
                #rs.DeleteObject(o.guid)
            else:
                #print('unable to delete {}'.format(o.name))
                pass


    def delete_name(self, name):
        for o in self.data:
            if o.name == name:
                if isinstance(o, Geometry):
                    #self.delete(o)
                    o.delete()
                # elif isinstance(o, NameGroup):
                #     for n in o.names:
                #         delete_name(n)

    def replace(self, index, obj):
        try:
            id = self.data[index].guid
            rs.DeleteObject(id)
        except:
            print('failed to delete object ', id)

        self.data[index] = obj

    def rename(self, name, out_name):
        objs= self.get_by_name(name)
        basket = []
        for o in objs:
            o.name = out_name
            #TODO: check other types such as groups for renaming
            try:
                rs.ObjectName(o.guid,out_name)
            except:
                pass
            basket.append(o)
        return basket

def _str_vects(vects):
    txt = ''
    for v in vects:
        t = '(%4.1f,%4.2f,%4.2f) ' % (v[0], v[1], v[2])
        txt += t
    return txt

def enable_print_steps(flag):
    PRINTSTEPS=flag

def enable_add_steps(flag):
    ADDSTEPS=flag

def colorize(name=None,color=None):
    print(ENGINE.name_list)
    if name:
        #colorize objs of a given name
        pass
    elif name is None:
        if color is None:
            cwh=rtc.ColorWheel()
        for n in ENGINE.name_list:
            if color is None:
                color=cwh.get_next()
            objs=ENGINE.get_by_name(n)
            for o in objs:
                o.color=color







def enable_redraw(flag):
    ENABLEDARAW=flag
    ENGINE.enable_redraw(flag)

def clear_doc():
    ENGINE.clear_doc()

def empty_trash():
    ENGINE.delete_name('trash')

def delete_name(name):
    ENGINE.delete_name(name)

def unstage_name(name):
    ENGINE.unstage_name(name)

def rename(name,out_name):
    return ENGINE.rename(name,out_name)

def add_rhino_box(name,given_name=None):
    objs = rs.ObjectsByName(name)
    if len(objs) > 0:
        for id in objs:
            flag, org_vect = rtf.is_solid_box(id)
            org=org_vect[0]
            vvect=org_vect[1]
            uvect=org_vect[2]
            wvect=org_vect[3]

            u = rs.VectorUnitize(uvect)
            v = rs.VectorUnitize(vvect)
            w = rs.VectorUnitize(wvect)

            su= rs.VectorLength(uvect)
            sv = rs.VectorLength(vvect)
            sw = rs.VectorLength(wvect)

            size = Vector3d(su, sv, sw)
            position=Point3d(org)
            vects=[u,v,w]
            if given_name:
                iname=given_name
            else:
                iname=name
            box=create_box(size,position,vects,iname)
            ENGINE._hide_rhino_object(id)



def create_box(size=Vector3d(1, 1, 1), position=Point3d(0, 0, 0),
               vects=[Vector3d(1, 0, 0), Vector3d(0, 1, 0), Vector3d(0, 0, 1)],
               name='default', parent=None,normals=None):
    #print('position-=',position, '\nvects[0]=', Point3d(vects[0]), '\nvects[1]=',Point3d(vects[1]))
    size=Vector3d(size[0],size[1],size[2])
    plane = Plane(Point3d(position), vects[0], vects[1])
    box_id = rtm.create_mesh_box(position, vects, size, normals)
    rs.ObjectName(box_id, name)
    object = Geometry(box_id, position, vects, size, None, name, parent)
    ENGINE.add(object)
    rs.ObjectLayer(object.guid, GENLAYER)
    return object

def group(names, out_name):
    group_object = NameGroup(names, out_name)
    ENGINE.add(group_object)

def divide(name, divs=[0.5, 0.5], out_names=['box_A'],
           direction=0, ratio_mode=True, delete_input=True,
           min_size=None, recursion_count=0,
           recursion_max=100, force_recursion=False, module=None):
    rs.EnableRedraw(False)
    out_guid=[]
    if isinstance(name, basestring):
        objs = ENGINE.get_by_name(name)
        if objs and isinstance(objs[0], NameGroup):
            for g in objs:
                for n in g.names:
                    extended_names = []
                    for oname in out_names:
                        if oname == g.name:
                            oname = n
                        else:
                            oname = n + '.' + oname
                        extended_names.append(oname)
                    out_guid += divide(n, divs, extended_names, direction, ratio_mode, delete_input,
                           min_size, recursion_count, recursion_max, force_recursion)
            return []
    elif isinstance(name, list):
        if isinstance(name[0], Geometry):
            objs = name
            name = objs[0].name
        else:
            return []
    else:
        return []

    #print('size of objs=',len(objs))
    # for each given object
    for o in objs:
        # terminal conditions:
        if min_size is not None:
            if o.size[direction] < min_size:
                # print('terminal con: size less then given minimum')
                continue

        if not ratio_mode:
            if o.size[direction] < divs[0]:
                # print('terminal con: size less then first div width')
                continue

        # actual rule body
        #if divs[-1] == 'r':
        #    length = o.size[direction]
        #    adj_divs = _get_recursive_ratios(length, divs, ratio_mode)
        #else:
        #    adj_divs = divs
        length = o.size[direction]
        adj_divs,out_names=_cap_divs(length,divs,name, out_names, ratio_mode, module)


        out_objs = _divide_object(ENGINE, o, adj_divs, out_names, direction, ratio_mode)
        #print('---out objs size:',len(out_objs))
        sel = []
        for oo in out_objs:
            out_guid.append(oo.guid)
            if oo.name == name:
                sel.append(oo)

        # recursion
        if min_size is None:
            min_size = 1
        if len(sel) > 0:
            if recursion_count < recursion_max:
                out_guid += divide(sel, divs, out_names, direction, ratio_mode, True,
                       min_size=min_size,
                       recursion_count=recursion_count + 1)
            else:
                # print('exceeded recursion max')
                continue
        else:
            # print('name not found for recursion')
            pass

    if delete_input:
        ENGINE.unstage_objects(objs)
    else:
        for o in objs:
            o.hide()

    if TAKESNAPSHOTS:
        ENGINE._snap_shot()
    if ENABLEDARAW:
        rs.EnableRedraw(True)
    return out_guid

def divide_u_count(name, divs, out_name):

    pass
def divide_face_u(name, width, stretch=False):
    pass
def divide_face_uv(name, width, height, out_name, stretch_u=True, stretch_v=True):
    objs, indice = ENGINE.get_by_name(name, return_index=True)
    basket = []
    for o in objs:
        mesh=rs.coercemesh(o.guid)
        W,H,U,V=rtm.get_face_info(mesh)
        # W: total width
        # H: total height
        # U: u_vect
        # V: v_vect
        if height:
            if stretch_v:
                count_v = int( round (H / height) )
                div_h = H / count_v
        else:
            count_v= 1
            div_h = H

        if width:
            count_u = int( round (W / width))
            div_w = W / count_u
        else:
            count_u = 1
            div_w = W

        u=U*div_w
        v=V*div_h
        vects = [U, V, rs.VectorCrossProduct(U,V)]
        size=Vector3d(div_w,div_h,0)
        face_count=0
        faces=[]
        for i in range(count_v):
            for j in range(count_u):
                face_count+=1
                offset = (U * (j*div_w)) + (V * (i*div_h))
                nface=rtm.scale_face(mesh,[div_w,div_h],ratio_mode=False,offset=offset)
                pos=Point3d(mesh.Vertices[0])+offset
                geoface=GeoFace(nface,pos,vects,size)
                geoface.name=out_name
                rs.ObjectName(nface,out_name)
                rs.ObjectLayer(nface,GENLAYER)
                # faces.append(nface)
                ENGINE.add(geoface)
        o.unstage()

        #rs.ShowObjects(faces)
    ENGINE.add_step('{} -> divide_face_uv -> {}'.format(name,out_name))
    #pass

def box_on_face_center(facename,u,v,w,out_name):
    objs = ENGINE.get_by_name(facename)
    basket = []
    for o in objs:
        mesh = rs.coercemesh(o.guid)
        center=(mesh.Vertices[0]+mesh.Vertices[1])
        center=Point3d(center.X,center.Y,center.Z)*0.5
        center -= Point3d(u/2,-v/4,0)
        create_box(Vector3d(u,v,w),center,name=out_name)

        basket.append(center)
    return basket

def divide_x(name, divs, out_name, ratio_mode=None, delete_input=True):
    if ratio_mode is None:
        if divs[0] > 1:
            ratio_mode = False
        else:
            ratio_mode = True
    direction = 0

    out_guid = divide(name, divs, out_names=out_name,
           direction=direction, ratio_mode=ratio_mode, delete_input=delete_input,
           min_size=None, recursion_count=0,
           recursion_max=100, force_recursion=False)

    ENGINE.add_step('{} -> divide_x ->{}:{}'.format(name,out_name,len(out_guid)))



def divide_y(name, divs, out_name, ratio_mode=None, delete_input=True):
    if ratio_mode is None:
        if divs[0] > 1:
            ratio_mode = False
        else:
            ratio_mode = True
    direction = 1

    out_guid = divide(name, divs, out_names=out_name,
           direction=direction, ratio_mode=ratio_mode, delete_input=delete_input,
           min_size=None, recursion_count=0,
           recursion_max=100, force_recursion=False)

    ENGINE.add_step('{} -> divide_y ->{}:{}'.format(name,out_name,len(out_guid)))

def divide_z(name, divs, out_name, ratio_mode=None, delete_input=True):
    if ratio_mode is None:
        if divs[0] > 1:
            ratio_mode = False
        else:
            ratio_mode = True
    direction = 2

    out_guid = divide(name, divs, out_names=out_name,
           direction=direction, ratio_mode=ratio_mode, delete_input=delete_input,
           min_size=None, recursion_count=0,
           recursion_max=100, force_recursion=False)

    ENGINE.add_step('{} -> divide_z ->{}:{}'.format(name,out_name,len(out_guid)))


def _divide_eq(name,w,out_names,direction='z'):
    objs=ENGINE.get_by_name(name)
    for o in objs:
        divs=[]
        if direction=='z':
            count=round(o.size[2]/w)
            aw=o.size[2]/count
            divs=[]
            for i in range(count):
                divs.append(aw)
        _divide_object(ENGINE,o,divs,out_names,direction,ratio_mode=False,)
    ENGINE.add_step('{} -> divide_eq ->{}'.format(name,out_names))


def divide_mx(name,div,out_names,ratio_mode=True):
    _divide_mirror(name,div,out_names,'x',ratio_mode)

def divide_my(name,div,out_names,ratio_mode=True):
    _divide_mirror(name,div,out_names,'y',ratio_mode)

def _divide_mirror(name,div,out_names,direction='x',
                  ratio_mode=True,delete_input=True):
    objs = ENGINE.get_by_name(name)
    left = '_1100'
    right = '_2200'
    middle = '_3200'
    for o in objs:
        if ratio_mode:
            length=1.0
        else:
            length=o.size(direction)
        if div<length/2:
            divs=[div,length-(div*2),div]
            tempnames = [left, middle, right]
        else:
            divs=[length/2,length/2]
            tempnames = [left, right]

        #print(divs)
        basket=_divide_object(ENGINE, o, divs, tempnames, direction, ratio_mode)
        basket[-1].invert(direction, copy=False)

        ENGINE.unstage_object(o)
        #o.unstage()
        #print(str(basket[-1]))

        i = 0
        for name in tempnames:
            j=i%len(out_names)
            oname=out_names[j]
            ENGINE.rename(name,oname)
            i+=1

    ENGINE.add_step('{} -> divide_m{} ->{}'.format(name,direction,out_names))

def invert_x(name):
    _invert(name,'x')

def invert_y(name):
    _invert(name,'y')

def _invert(name, direction='x'):
    objs=ENGINE.get_by_name(name)
    for o in objs:
        if isinstance(o,Geometry):
            mirrored=o.invert(direction,copy=True)
            ENGINE.add(mirrored)
            #ENGINE.delete(o)
            o.unstage()
    ENGINE.add_step('{} -> invert_{}'.format(name,direction))




def scale(name, scales, alignment=Align.NW, out_name=None):
    objs, indice = ENGINE.get_by_name(name, return_index=True)
    basket = []
    for o, i in zip(objs, indice):
        if isinstance(o, NameGroup):
            for n in o.names:
                basket += scale(n,scales,alignment,out_name)
        else:

            shape = _scale(o, scales, alignment)
            if out_name is None:
                adj_out_name=name
                ENGINE.unstage_object(o)
                #o.unstage()
                #rs.HideObject(o.guid)
            else:
                adj_out_name=out_name

            shape.name=adj_out_name
            shape.set_parent(o)
            rs.ObjectName(shape.guid,adj_out_name)
            #why without the line below can create geometries?
            #ENGINE.add(shape)
            basket.append(shape)
    return basket


def _scale(obj, scales, alignment=Align.NW, size=None):
    # print('ps size:{}'.format(size))
    o = obj
    org = o.position
    u = o.get_vect(0)
    v = o.get_vect(1)
    w = o.get_vect(2)

    ou = u * o.size[0]
    ov = v * o.size[1]

    if size:
        su = u * size[0]
        sv = v * size[1]
    else:
        su = ou * scales[0]
        sv = ov * scales[1]

    du = su - ou
    dv = sv - ov

    mu = ((su - ou) / 2)
    mv = ((sv - ov) / 2)

    if alignment == Align.SW:
        pass
    elif alignment == Align.NW:
        org -= dv
    elif alignment == Align.SE:
        org = org - du
    elif alignment == Align.NE:
        org = org - du - dv
    elif alignment == Align.M:
        org = org - mu - mv
    elif alignment == Align.S:
        org = org - mu
    elif alignment == Align.N:
        org = org - dv - mu
    elif alignment == Align.E:
        org = org - du - mv
    elif alignment == Align.W:
        org -= mv

    # print('centered:', centered, list(org))
    pos = org
    vects = [u, v, w]
    if size:
        scales=Vector3d(size[0] / o.size[0],
                        size[1] / o.size[1],
                        size[2] / o.size[2],
                        )
    else:
        size = Vector3d(o.size[0] * scales[0],
                        o.size[1] * scales[1],
                        o.size[2] * scales[2])

    # print('ps size:{}'.format(size))
    # print('pos=',pos)
    ref = [o.position, o.position+o.vects[0]]
    #ref = [org,org+o.vects[0]]
    trg = [(0,0,0),(1,0,0)]
    dup = rs.OrientObject(obj.guid,ref,trg,1)
    dup = rs.ScaleObject(dup,(0,0,0),scales)
    dup = rs.OrientObject(dup,trg,ref)
    geo = Geometry(dup,o.position,vects,size)
    geo.move(org-o.position)
    geo.set_parent(o)
    ENGINE.add(geo)
    return geo


def _scale_worked(obj, scales, alignment=Align.NW, size=None):
    # print('ps size:{}'.format(size))
    o = obj
    org = o.position
    u = o.get_vect(0)
    v = o.get_vect(1)
    w = o.get_vect(2)

    ou = u * o.size[0]
    ov = v * o.size[1]

    if size:
        su = u * size[0]
        sv = v * size[1]
    else:
        su = ou * scales[0]
        sv = ov * scales[1]

    du = su - ou
    dv = sv - ov

    mu = ((su - ou) / 2)
    mv = ((sv - ov) / 2)

    if alignment == Align.SW:
        pass
    elif alignment == Align.NW:
        org -= dv
    elif alignment == Align.SE:
        org = org - du
    elif alignment == Align.NE:
        org = org - du - dv
    elif alignment == Align.M:
        org = org - mu - mv
    elif alignment == Align.S:
        pass
    elif alignment == Align.N:
        org = org - dv
    elif alignment == Align.E:
        org = org - du - mv
    elif alignment == Align.W:
        org -= mv

    # print('centered:', centered, list(org))
    pos = org
    vects = [u, v, w]
    if not size:
        size = Vector3d(o.size[0] * scales[0],
                        o.size[1] * scales[1],
                        o.size[2] * scales[2])
    # print('ps size:{}'.format(size))
    # print('pos=',pos)

    box = create_box(size, pos, vects)
    #box.guid=inverse_mesh(box.guid,True)

    return box


def scale_x(name, scale_num, alignment=Align.NW, out_name=None):
    output=scale(name,[scale_num,1,1],out_name=out_name, alignment=alignment)
    ENGINE.add_step('{} -> scale_x'.format(name))
    return output

def scale_y(name, scale_num, alignment=Align.NW, out_name=None):
    output =scale(name,[1,scale_num,1],out_name=out_name, alignment=alignment)
    ENGINE.add_step('{} -> scale_y'.format(name))
    return output

def scale_z(name, scale_num, alignment=Align.NW, out_name=None):
    output =scale(name,[1,1,scale_num],out_name=out_name, alignment=alignment)
    ENGINE.add_step('{} -> scale_z'.format(name))
    return output

def decompose(name,out_names=['*_SN,*_EW']):
    pass

def extract_face(name,direction='S',out_name=None,add_step=True):
    if out_name is None:
        out_name=name+'_face_'+direction
    objs = ENGINE.get_by_name(name)
    basket=[]
    for o in objs:
        faces=o.extract_face(direction)
        for f in faces:
            f.name=out_name
            rs.ObjectName(f.guid,out_name)
            ENGINE.add(f)
            basket.append((f))
    if add_step:
        ENGINE.add_step('{} -> extract face {} ->{}'.format(name, direction,out_name))
    return basket

def decompose_2(name, out_names=['H','V'], name_as_prefix=True):
    if len(out_names)<2:
        print('please give at lease 2 names or leave as default')
    faces=_decompose_sides(name)
    for i in range(len(out_names)):
        if name_as_prefix:
            out_names[i] = '{}_{}'.format(name,out_names[i])

    for s in ['T','B']:
        rename('{}_{}'.format(name,s),out_names[0])
    for s in ['S','N','W','E']:
        rename('{}_{}'.format(name,s),out_names[1])
    ENGINE.add_step('{}-> decompose ->{}'.format(name,out_names))

def decompose_3(name, out_names=['SIDES','TOP','BOT'], name_as_prefix=True):
    if len(out_names)<3:
        print('please give at lease 3 names or leave as default')

    _decompose_sides(name)
    for i in range(len(out_names)):
        if name_as_prefix:
            out_names[i] = '{}_{}'.format(name,out_names[i])

    for s in ['S','N','W','E']:
        ENGINE.rename('{}_{}'.format(name,s),out_names[0])
    ENGINE.rename('{}_{}'.format(name, 'top'), out_names[1])
    ENGINE.rename('{}_{}'.format(name, 'bot'), out_names[2])
    ENGINE.add_step('{}-> decompose ->{}'.format(name, out_names))

def decompose_4(name, out_names=['SN','EW','top','bot'], name_as_prefix=True):
    if len(out_names)<4:
        print('please give at lease 4 names or leave as default')
    _decompose_sides(name)
    for i in range(len(out_names)):
        if name_as_prefix:
            out_names[i] = '{}_{}'.format(name,out_names[i])
    sides=[['S','N'],['E','W'],['T'],['B']]
    for i in range(len(sides)):
        for s in sides[i]:
            print('{}_{}'.format(name,s),'->',out_names[i])
            ENGINE.rename('{}_{}'.format(name,s),out_names[i])
    ENGINE.add_step('{}-> decompose ->{}'.format(name, out_names))

def decompose(name, out_names=['S','N','W','E','top','bot'], name_as_prefix=True):
    if len(out_names)<6:
        print('please give at lease 6 names or leave as default')
    _decompose_sides(name)
    for i in range(len(out_names)):
        if name_as_prefix:
            out_names[i] = '{}_{}'.format(name,out_names[i])
    sides = ['S', 'N', 'E', 'W', 'T', 'B']
    for i in range(len(sides)):
        s=sides[i]
        ENGINE.rename('{}_{}'.format(name, s), out_names[i])
    ENGINE.add_step('{}-> decompose ->{}'.format(name, out_names))

def _decompose_sides(name,sides=['S','N','W','E','T','B'],out_names=None,unstage_input=True):
    if out_names is None:
        out_names = sides
    for i in range(len(out_names)):
        out_names[i]=name+'_'+out_names[i]

    faces={}
    for s,oname in zip(sides,out_names):
        faces[s]=extract_face(name,s,oname,add_step=False)
    if unstage_input:
        print('unstaging {}'.format(name))
        ENGINE.unstage_name(name)
    return faces

def unstage_components(name):
    pass

def component_on_face(facename,compname,out_name='terminal'):
    if facename in ENGINE._mapped_components:
        ENGINE._mapped_components[facename].unstage()

    group,w,h=ENGINE.get_imported_component(compname)
    faceobjs=ENGINE.get_by_name(facename)
    output=[]
    compobjs=rs.ObjectsByGroup(group)

    for o in faceobjs:
        ccomp=rs.CopyObjects(compobjs)
        rs.RemoveObjectsFromGroup(ccomp, group)
        output += _component_on_face(ccomp,w,h,o)
        o.hide()
    newgroup = rs.AddGroup()
    rs.AddObjectsToGroup(output,newgroup)
    ggroup=GeoGroup(newgroup)
    ggroup.name=out_name
    ENGINE._mapped_components[facename]=ggroup
    ENGINE.add(ggroup)
    ENGINE.add_step('{} -> is mapped to ->{}'.format(facename, compname))

def _component_on_face(objs,w,h,faceobject):
    # TODO: later transfer this methos to rtm
    meshface = rs.coercemesh(faceobject.guid)
    #print(faceobject.vects[1][1])
    #W=faceobject.size[0]
    #H=faceobject.size[2]
    U=faceobject.vects[0]
    N=faceobject.vects[2]
    W=faceobject.size[0]
    H=faceobject.size[1]
    #W, H, trash, trash2= rtm.get_face_info(meshface)
    flipz=False
    flipy=False
    if U[0] == -1 :
        flipz=True


    n = rs.VectorCrossProduct(U, N)

    # if n[2]>0:
    #     flipy=True
    if n[2]>0 :
            flipy=True
            if U[0] == -1:
                flipy=False

    position=Point3d(meshface.Vertices[0])
    scale_u=W/w
    scale_v=H/h
    #objs = rs.ObjectsByGroup(group)
    rs.ScaleObjects(objs,(0,0,0),(scale_u,1,scale_v))
    reference = [(0,0,0),(1,0,0)]
    target=[faceobject.position, faceobject.position+U]
    #target = [Point3d(meshface.Vertices[0]),Point3d(meshface.Vertices[1])]
    output=[]
    for o in objs:
        if flipz:
            rs.ScaleObject(o,(0,0,0),(1,1,-1))
        if flipy:
            rs.ScaleObject(o,(0,0,0),(1,-1,1))
        oriented=rs.OrientObject(o,reference,target,0)

        output.append(oriented)
    return output

def import_component(filename,out_name):
    if out_name is None:
        out_name=filename
    group,w,h=_import(filename)
    ENGINE.add_imported_component(out_name,group,w,h)

def _import(file):
    filename=ENGINE._path+file+'.3dm'
    rs.UnselectAllObjects()
    rs.Command('!_-import {} enter'.format(filename))
    objs=rs.LastCreatedObjects()
    g = rs.AddGroup()
    rs.AddObjectsToGroup(objs, g)

    ref = None
    for o in objs:
        if rs.ObjectName(o) == 'ref':
            ref = o
            break
    if ref is None:
        print("imported file must contain a 4 pointed polyline named 'ref' ")
    rps = rs.CurvePoints(ref)
    w = rps[1].DistanceTo(rps[0])
    h = rps[3].DistanceTo(rps[0])
    rs.DeleteObject(ref)
    return g,w,h

def duplicate(name,out_name,transform=[0,0,0]):
    objs=ENGINE.get_by_name(name)
    dups=[]

    for o in objs:
        if isinstance(o, Geometry):
            #print(o.name, o.guid)
            dup=o.clone()
            #print('----',dup.name,dup.guid)
            dup.name=out_name
            rs.ObjectName(dup.guid,out_name)
            #print('----',dup.name, dup.guid)
            dup.position = rs.VectorAdd(dup.position,transform)
            rs.MoveObject(dup.guid, transform)
            dups.append(dup)
    ENGINE.add_step('{} -> duplicate ->{}:{}'.format(name, out_name, len(dups)))
    return dups

def reset():
    global ENGINE
    SAVEFILENAME = None
    ENABLEDARAW=False

    try:
        ENGINE.ui.Close()
    except Exception as e: print(e)

    try:
        enable_redraw(False)
        clear_doc()
        ENGINE._reset()
    except:
        ENGINE = Engine()

    rs.CurrentLayer(GENLAYER)
    rs.EnableRedraw(True)
    ENABLEDARAW=True
    ENGINE.show_ui()
    #enable_redraw(True)
    #ENGINE.add_step('start')

def start():
    enable_redraw(False)

def end():
    ENGINE.add_step('end')
    ENGINE._dettach_rhino_events()
    enable_redraw(True)
    rs.EnableRedraw(True)
    #ENGINE.show_ui()

def hide_name(name):
    sel = ENGINE.get_by_name(name)
    for o in sel:
        o.unstage()

def move_ratio(name,transform=[0,0,0],out_name=None):
    _move(name,transform,out_name,True)
    ENGINE.add_step('{} -> move ratio'.format(name))

def move(name,transform=[0,0,0],out_name=None):
    _move(name,transform,out_name,False)
    ENGINE.add_step('{} -> move meters'.format(name))

def _move(name,transform=[0,0,0],out_name=None, ratio_mode=False):

    sel = ENGINE.get_by_name(name)
    print('got selection size:',len(sel))
    if sel is None or len(sel) < 1:
        print('\"' + name + '\" is not defined')
    for o in sel:
        vects=o.vects
        if ratio_mode:
            adj_transform =(transform[0]*o.size[0]*vects[0]-
                            transform[1]*o.size[1]*vects[1]+
                            transform[2]*o.size[2]*vects[2])
        else:
            adj_transform = (transform[0]*vects[0]-
                             transform[1]*vects[1]+
                             transform[2]*vects[2])

        dup=o.clone()
        dup.position += adj_transform
        rs.MoveObject(dup.guid,adj_transform)
        if out_name:
            dup.name = out_name

        ENGINE.unstage_object(o)


def set_x(name,num,alignment=Align.NW):
    _set_size(name,num,None,None,alignment)
    ENGINE.add_step('{} -> set_x'.format(name))

def set_y(name,num,alignment=Align.NW):
    _set_size(name,None,num,None,alignment)
    ENGINE.add_step('{} -> set_y'.format(name))

def set_z(name,num,alignment=Align.NW):
    _set_size(name,None,None,num,alignment)
    ENGINE.add_step('{} -> set_z'.format(name))

def _set_size(name,x=None,y=None,z=None,alignment=Align.NW):

    sel = ENGINE.get_by_name(name)
    if sel is None or len(sel) < 1:
        print('\"' + name + '\" is not defined')
    basket=[]
    for o in sel:
        if x is None:
            x = o.size[0]
        if y is None:
            y = o.size[1]
        if z is None:
            z = o.size[2]
        print(x,y,z)
        shape=_scale(o,None,alignment,size=Vector3d(x,y,z))
        ENGINE.unstage_object(o)
        shape.name=name
        ENGINE.add(shape)
    return basket


def _cap_divs(length,divs,name,out_name,ratio_mode=True, module=None):
    total=0
    adj_divs=[]
    #divs = divs[:-1]
    keep_r=False
    if ratio_mode:
        length=1

    for d in divs:
        if d=='r':
            div = length - total
            adj_divs.append(div)
            break
        elif total+d>=length:
            div=length-total
            adj_divs.append(div)
            if total+d>length:
                keep_r=True
            break
        else:
            adj_divs.append(d)
            total += d
    if keep_r:
        if len(out_name) == len(divs):
            out_name[-1]=name
        else:
            print('--! length of out-name and divs are different')
    return adj_divs, out_name


def _get_recursive_ratios(length, divs, ratio_mode=True):
    divs = divs[:-1]
    if length == 0:
        print('length is zero')
        return

    total = 0
    for div in divs:
        total += div
    if total < length:
        if ratio_mode:
            last = 1 - total
            divs.append(last)
        else:
            last = length - total
            divs.append(last)
    return divs


def _divide_object(engine, obj, divs, out_names, direction='x', ratio_mode=True, keep_r=False):
    if direction=='x':
        direction=0
    elif direction == 'y':
        direction=1
    elif direction == 'z':
        direction=2

    unitize = not ratio_mode
    adj_divs = divs
    o = obj
    basket = []
    trans = Vector3d(0, 0, 0)
    for i in range(len(adj_divs)):
        div = adj_divs[i]
        j = i % len(out_names)

        # scales
        scales = [1, 1, 1]
        scales[direction] = div
        if not ratio_mode:
            scales[direction]=div/o.size[direction]

        if i > 0:
            trans += o.get_vect(direction, unitize) * adj_divs[i - 1]

        oname = out_names[j]
        dupo=_scale(o,scales,Align.SW)
        dupo.move(trans)
        dupo.name=oname
        #dupo.set_parent(o)
        basket.append(dupo)
    return basket


def short_guid(guid):
    if guid:
        guid=str(guid)
        if len(guid)>6:
            return (guid[:3]+guid[-3:])
    return['000000']

def check_face(name):
    faceobjs=ENGINE.get_by_name(name)
    for o in faceobjs:
        meshface=rs.coercemesh(o.guid)
        rs.AddPoint(meshface.Vertices[3])

def draw_axies(name):
    faceobjs = ENGINE.get_by_name(name)
    for o in faceobjs:
        #mf = rs.coercemesh(o.guid)
        mf=o
        u_axis=rs.AddLine(mf.position,mf.position+mf.vects[0])
        v_axis=rs.AddLine(mf.position,mf.position+mf.vects[1])
        n_axis=rs.AddLine(mf.position,mf.position+mf.vects[2])
        rs.ObjectColor(u_axis, (255,0,0))
        rs.ObjectColor(v_axis, (0, 255, 0))
        rs.ObjectColor(n_axis, (0, 0, 255))

        n = rs.VectorCrossProduct(mf.vects[0],mf.vects[2])
        if n[2]>0:
            rs.AddPoint(mf.position)

def inverse_mesh(meshid, delete_input=False):
    verts=rs.MeshVertices(meshid)
    faces=rs.MeshFaceVertices(meshid)
    normals=rs.MeshVertexNormals(meshid)

    print('verts:',verts)
    print('faces:',faces)
    print('normals:',normals)

    inormals=[]
    for n in normals:
        inormal=rs.VectorScale(n,-1)
        inormals.append(inormal)
    inverted=rs.AddMesh(verts,faces,inormals)
    if delete_input:
        rs.DeleteObject(meshid)
    return inverted