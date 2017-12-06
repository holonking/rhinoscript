
import rhinoscriptsyntax as rs
import Rhino
from Rhino.Geometry import *
import RsTools.MeshTools as rtm

CLEAR_ON_RESET=False
GENLAYER='SHAPE_GRAMMAR_GENERATED_OBJECTS'
GENHIDDEN='SHAPE_GRAMMAR_GENERATED_HIDDEN'
ENABLEDARAW=False
TAKESNAPSHOTS=False

rs.AddLayer(GENLAYER)
rs.AddLayer(GENHIDDEN)
class Geometry():
    def __init__(self, guid, position=None, vects=None,
                 size=None, rotation=None, name='',parent=None):
        self.guid=guid
        self.name=name
        self.size=Vector3d(size) if size is not None else Vector3d(3,3,3)
        self.position=Point3d(position) if position is not None else Point3d(0,0,0)
        self.rotate=Vector3d(rotation) if rotation is not None else Vector3d(0,0,0)
        self.vects=[]
        for v in vects:
            self.vects.append(Vector3d(v))
        self.plane=Plane(self.position,self.vects[0],self.vects[1])
        self._parent=parent
        if parent is not None:
            self.set_parent(parent)
        self.children = []

    def __str__(self):
        return '{}<vects:({},{})>'.format(self.name,_str_vects(self.vects),list(self.size))
        #return '{}<pos:({}),size:{},vectsu:({}),id:{}>'.format(
        #    self.name, self.position,self.size,self.vects[0],self.guid)

    def print_tree(self,level=0):
        prefix='        '*level
        print(prefix+str(self))
        for c in self.children:
            c.print_tree(level+1)

    @property
    def root(self):
        if self._parent is None:
            return self
        return self._parent.root

    def set_parent(self,parent):
        self._parent=parent
        self._parent.children.append(self)

    def get_shape(self, guid):
        #override
        pass

    def get_vect(self,direction, unitized=True):
        if unitized:
            return self.vects[direction]
        else:
            return self.vects[direction]*self.size[direction]

class NameGroup():
    def __init__(self, names,group_name):
        self.names=names
        self.name=group_name
    def get_objects(self):
        basket=[]
        for name in self.names:
            objs=ENGINE.get_by_name(name)
            if objs:
                basket+=objs
        return basket

class Engine():
    #system
    def __init__(self):
        self.data = []

    def _snap_shot(self):
        pass

    def clear_doc(self):
        trash = rs.ObjectsByLayer(GENLAYER)
        if len(trash) > 0:
            rs.DeleteObjects(trash)

    def enable_snap_shot(self, flag=True):
        TAKESNAPSHOTS = flag

    def add(self, obj):
        self.data.append(obj)

    def add_multiple(self, objs):
        self.data += objs

    def delete(self, obj):
        index = self.data.index(obj)
        if index > 0:
            del self.data[index]
        try:
            rs.DeleteObject(obj.guid)
            obj.guid = None
        except:
            print('unable to delete')
            pass

    def print_data(self):
        for o in self.data:
            print(o)

    def print_tree(self):
        for o in self.data:
            if o._parent is None:
                o.print_tree()

    def get_by_name(self,name, return_index=False):
        basket=[]
        indice=[]
        for i in range(len(self.data)):
            o=self.data[i]
            if o.name==name:
                basket.append(o)
                indice.append(i)
        if return_index:
            return basket,indice
        return basket

    def delete_objects(self, objs):
        for o in objs:
            i=self.data.index(o)
            if i>0:
                del self.data[i]
                rs.DeleteObject(o.guid)

    def delete_name(self,name):
        for o in self.data:
            if o.name==name:
                self.delete(o)

    def replace(self,index,obj):
        try:
            id=self.data[index].guid
            rs.DeleteObject(id)
        except:
            print('failed to delete object ',id)

        self.data[index]=obj

    def rename(self,name,out_name):
        objs, indice = self.get_by_name(name, return_index=True)
        basket = []
        for o in objs:
            o.name=out_name
            basket.append(o)
        return basket


ENGINE=Engine()

def _str_vects(vects):
    txt=''
    for v in vects:
        t='(%4.1f,%4.2f,%4.2f) '%(v[0],v[1],v[2])
        txt+=t
    return txt


def create_box(size=Vector3d(1, 1, 1), position=Point3d(0, 0, 0),
               vects=[Vector3d(1, 0, 0), Vector3d(0, 1, 0), Vector3d(0, 0, 1)],
               name='default', parent=None):

    plane = Plane(position, vects[0], vects[1])
    box_id = rtm.create_mesh_box(plane, size)
    rs.ObjectName(box_id,name)
    object = Geometry(box_id, position, vects, size, None, name, parent)
    ENGINE.add(object)
    rs.ObjectLayer(object.guid, GENLAYER)
    return object

def group(names,out_name):
    group_object=NameGroup(names,out_name)
    ENGINE.add(group_object)

def divide(name, divs=[0.5, 0.5], out_names=['box_A'],
           direction=0, ratio_mode=True, delete_input=True,
           min_size=None, recursion_count=0,
           recursion_max=100, force_recursion=False):
    print(type(name),name)
    rs.EnableRedraw(False)

    if isinstance(name, basestring):
        objs = ENGINE.get_by_name(name)
        print(type(objs), objs)
        if isinstance(objs, NameGroup):
            print('is group',objs)
            for n in name.names:
                extended_name = []
                for oname in out_names:
                    extended_name.append(n + '.' + oname)
                divide(n, divs, extended_name, direction, ratio_mode, delete_input,
                       min_size, recursion_count, recursion_max, force_recursion)
    elif isinstance(name, list):
        if isinstance(name[0], Geometry):
            objs = name
            name = objs[0].name
    else:
        return

    return

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
        if divs[-1] == 'r':
            length = o.size[direction]
            adj_divs = _get_recursive_ratios(length, divs, ratio_mode)
        else:
            adj_divs = divs
        out_objs = _divide_object(ENGINE, o, adj_divs, out_names, direction, ratio_mode)

        sel = []
        # print(out_names)
        for oo in out_objs:
            if oo.name == name:
                sel.append(oo)

        # recursion
        if min_size is None:
            min_size = 1
        if len(sel) > 0:
            if recursion_count < recursion_max:
                divide(sel, divs, out_names, direction, ratio_mode, True,
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
        ENGINE._snap()
    if ENABLEDARAW:
        rs.EnableRedraw(True)

def divide_x(name,divs,out_name,ratio_mode=None,delete_input=True):
    if ratio_mode is None:
        if divs[0]>1:
            ratio_mode=False
        else:
            ratio_mode = True
    direction=0

    divide(name, divs, out_names=out_name,
           direction=direction, ratio_mode=ratio_mode, delete_input=delete_input,
           min_size=None, recursion_count=0,
           recursion_max=100, force_recursion=False)


def divide_y(name, divs, out_name, ratio_mode=None, delete_input=True):
    if ratio_mode is None:
        if divs[0] > 1:
            ratio_mode = False
        else:
            ratio_mode = True
    direction = 1

    divide(name, divs, out_names=out_name,
           direction=direction, ratio_mode=ratio_mode, delete_input=delete_input,
           min_size=None, recursion_count=0,
           recursion_max=100, force_recursion=False)

def divide_z(name, divs, out_name, ratio_mode=None, delete_input=True):
    if ratio_mode is None:
        if divs[0] > 1:
            ratio_mode = False
        else:
            ratio_mode = True
    direction = 2

    divide(name, divs, out_names=out_name,
           direction=direction, ratio_mode=ratio_mode, delete_input=delete_input,
           min_size=None, recursion_count=0,
           recursion_max=100, force_recursion=False)

def _get_recursive_ratios(length, divs, ratio_mode=True):
    divs=divs[:-1]
    if length==0:
        print('length is zero')
        return

    total = 0
    for div in divs:
        total += div
    if total < length:
        if ratio_mode:
            last=1-total
            divs.append(last)
        else:
            last=length-total
            divs.append(last)
    return divs

def _divide_object(engine, obj, divs, out_names, direction, ratio_mode):
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


