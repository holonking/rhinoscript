import rhinoscriptsyntax as rs
import Rhino
from Rhino.Geometry import *
import RsTools.MeshTools as rtm
import shape_UI as shapeUI
reload(shapeUI)

CLEAR_ON_RESET = False
GENLAYER = 'SHAPE_GRAMMAR_GENERATED_OBJECTS'
GENHIDDEN = 'SHAPE_GRAMMAR_GENERATED_HIDDEN'
ENABLEDARAW = False
TAKESNAPSHOTS = False

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
        self.name = name
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
        self._staged=True

    def __str__(self):
        return '{}<vects:({},{})>'.format(self.name, _str_vects(self.vects), list(self.size))
        # return '{}<pos:({}),size:{},vectsu:({}),id:{}>'.format(
        #    self.name, self.position,self.size,self.vects[0],self.guid)

    def print_tree(self, level=0):
        prefix = '        ' * level
        print(prefix + str(self))
        for c in self.children:
            c.print_tree(level + 1)

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

    def unstage(self):
        self._staged=False

    def stage(self):
        self._staged=True

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


class Engine():
    # system
    def __init__(self):
        self.data = []
        self.step=0
        self.step_texts=[]
        self.step_geometry=[]
        self._start_ui()
        self._enable_redraw=True

    def _start_ui(self):
        self.ui=shapeUI.ShapeForm()
        self.ui.slider.callbacks.append(self._slider_value_changed)
        self.ui.Show()

    def _slider_value_changed(self,value):
        #print('_slider_value_changed step:{}'.format(value))
        index=int(value)
        self.ui.tb_rules.Text = self._format_step_text(index+1)

        if self._enable_redraw:
            rs.EnableRedraw(False)
            for o in self.data:
                if isinstance(o,Geometry):
                    rs.HideObject(o.guid)
            rs.ShowObjects(self.step_geometry[index])
            rs.EnableRedraw(True)
        #self.ui.tb_rules.Text=str(value)
        #self.ui.tb_rules.Text='changed'

    def _snap_shot(self):
        pass

    def clear_doc(self):
        trash = rs.ObjectsByLayer(GENLAYER)
        if len(trash) > 0:
            rs.DeleteObjects(trash)

    def enable_redraw(self,flag=True):
        rs.EnableRedraw(flag)
        self._enable_redraw=flag
        if flag:
            rs.EnableRedraw(False)
            for o in self.data:
                if isinstance(o, Geometry):
                    rs.HideObject(o.guid)
            rs.ShowObjects(self.step_geometry[-1])
            rs.EnableRedraw(True)

    def add_step(self,text):
        print('{} | data count:{}'.format(text,len(self.data)))
        self.step_texts.append(text)
        current_objs=[]
        for o in self.data:
            if isinstance(o,Geometry) and o._staged:
                    current_objs.append(o.guid)
        self.step_geometry.append(current_objs)
        self.ui.slider.Value=self.step
        self.ui.slider.MaxValue=self.step
        self.step+=1

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

    def add_multiple(self, objs):
        self.data += objs

    def delete(self, obj):
        index = self.data.index(obj)
        if index >= 0:
            obj.unstage()
            rs.HideObject(obj.guid)
            #rs.ObjectLayer(obj.guid,GENHIDDEN)
        #    del self.data[index]
        # try:
        #     rs.DeleteObject(obj.guid)
        #     obj.guid = None
        # except:
        #     print('unable to delete')
        #     pass

    def print_data(self):
        for o in self.data:
            print(o)

    def print_tree(self):
        for o in self.data:
            if o._parent is None:
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
                    self.delete(o)
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
        objs, indice = self.get_by_name(name, return_index=True)
        basket = []
        for o in objs:
            o.name = out_name
            basket.append(o)
        return basket

ENGINE = Engine()

def _str_vects(vects):
    txt = ''
    for v in vects:
        t = '(%4.1f,%4.2f,%4.2f) ' % (v[0], v[1], v[2])
        txt += t
    return txt

def enable_redraw(flag):
    ENGINE.enable_redraw(flag)

def clear_doc():
    ENGINE.clear_doc()

def empty_trash():
    ENGINE.delete_name('trash')

def delete_name(name):
    ENGINE.delete_name(name)


def create_box(size=Vector3d(1, 1, 1), position=Point3d(0, 0, 0),
               vects=[Vector3d(1, 0, 0), Vector3d(0, 1, 0), Vector3d(0, 0, 1)],
               name='default', parent=None):
    plane = Plane(position, vects[0], vects[1])
    box_id = rtm.create_mesh_box(position, vects, size)
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
           recursion_max=100, force_recursion=False):
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
        adj_divs,out_names=_cap_divs(length,divs,name, out_names, ratio_mode)


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
        ENGINE.delete_objects(objs)
    else:
        for o in objs:
            rs.HideObject(o.guid)

    if TAKESNAPSHOTS:
        ENGINE._snap_shot()
    if ENABLEDARAW:
        rs.EnableRedraw(True)
    return out_guid

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
                ENGINE.delete(o)
                #o.unstage()
                #rs.HideObject(o.guid)
            else:
                adj_out_name=out_name

            shape.name=adj_out_name
            #why without the line below can create geometries?
            #ENGINE.add(shape)
            basket.append(shape)
    return basket

def scale_x(name, scale_num, alignment=Align.NW, out_name=None):
    scale(name,[scale_num,1,1],out_name=out_name, alignment=alignment)
    ENGINE.add_step('{} -> scale_x'.format(name))

def scale_y(name, scale_num, alignment=Align.NW, out_name=None):
    scale(name,[1,scale_num,1],out_name=out_name, alignment=alignment)
    ENGINE.add_step('{} -> scale_y'.format(name))

def scale_z(name, scale_num, alignment=Align.NW, out_name=None):
    scale(name,[1,1,scale_num],out_name=out_name, alignment=alignment)
    ENGINE.add_step('{} -> scale_z'.format(name))

def decompose(name,out_names=['*_SN,*_EW']):
    pass

def move(name,transform=[0,0,0],out_name=None):
    transform=Vector3d(transform[0], transform[1], transform[2])
    sel = ENGINE.get_by_name(name)
    if sel is None or len(sel) < 1:
        print('\"' + name + '\" is not defined')
    for o in sel:
        o.position += transform
        rs.MoveObject(o.guid,transform)
        if out_name:
            o.name = out_name

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
        ENGINE.delete(o)
        shape.name=name
        ENGINE.add(shape)
    return basket

def _scale(obj, scales, alignment=Align.NW, size=None):
    print('ps size:{}'.format(size))
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
    print('ps size:{}'.format(size))
    box = create_box(size, pos, vects)
    return box

def _cap_divs(length,divs,name,out_name,ratio_mode=True):
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
            print('--! length of out-anme and divs are different')
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


def _divide_object(engine, obj, divs, out_names, direction, ratio_mode, keep_r=False):
    unitize = not ratio_mode
    adj_divs = divs
    o = obj
    basket = []
    trans = Vector3d(0, 0, 0)
    for i in range(len(adj_divs)):
        div = adj_divs[i]

        j = i % len(out_names)

        # scales
        if ratio_mode:
            scales = [1, 1, 1]
            scales[direction] = div
            size = (scales[0] * o.size[0], scales[1] * o.size[1], scales[2] * o.size[2])
        else:
            size = [o.size[0], o.size[1], o.size[2]]
            size[direction] = div

        if i > 0:
            trans += o.get_vect(direction, unitize) * adj_divs[i - 1]

        oname = out_names[j]
        pos = o.position + Vector3d(trans[0], trans[1], trans[2])
        box = create_box(Vector3d(size[0], size[1], size[2]), pos, o.vects, oname)

        box.set_parent(o)
        basket.append(box)
    return basket
