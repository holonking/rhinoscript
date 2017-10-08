# -*- coding: utf-8 -*-
T='├─'
I='│'
L='└─'
D='─'
SELECT='█'
SPACE='   '
import os


def shortGuid(guid):
    if guid is None:return 'None'
    guid=str(guid)
    txt=str(guid[:2])+str(guid[-2:])
    return '['+txt+']'

def PrintException():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    print ('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))


class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        # super(AttrDict, self).__init__(*args, **kwargs)
        super(dict,self).__init__(*args, **kwargs)
        self.__dict__ = self

class PhaseObject():
    def __init__(self, parent=None,phase='None',guid=-1,*args, **kwargs):
        #super(AttrDict,self).__init__(*args, **kwargs)
        self.name='UnnamedPO'
        self.guid=guid
        self.children=[]
        self.parent=parent
        if parent is not None:
            self.set_parent(parent)
        self.phase=phase
        self.needUpdate=False
        self.level=0
        #usualy each surface has one type index
        self.typeIndex=0
        #during earlier stage,
        #a massing can have multiple index
        #by functionalities
        self.typeIndices=[0]*10
        self.is_selected=False
        self.description=''
    def __str__(self):
        txt=self.phase+'( {} )_{}'.format(len(self.children),self.typeIndex)
        if self.guid is not None:
            txt+=shortGuid(self.guid)
        return txt

    @property
    def root(self):
        if self.parent is not None:
            return self.parent.root
        return self

    def children_count(self):
        return len(self.children)

    def is_root(self):
        if self.parent is None:
            return True
        return False

    def is_end_node(self):
        if self.parent is None:return True
        index=self.parent.children.index(self)
        if index==len(self.parent.children)-1:return True
        return False

    def is_leaf(self):
        if self.children_count()==0:return True
        return False


    def find(self,name,val):
        if self.__dict__[name]==val:
            return self
        for c in self.children:
            o=c.find(name,val)
            if o is not None: return o
        return None

    def flattern(self,_bin=[]):
        _bin.append(self)
        #print(_bin)
        for c in self.children:
            _bin=c.flattern(_bin)
        return _bin

    def tree(self,is_end_node=True,starting_node=None,out_str='',_print=False):
        if starting_node is None:
            starting_node=self
        out_str=''
        prefix=''
        #else: prefix=' '+SPACE
        parent=self.parent
        if parent is not None and starting_node is not None:
            gparent=parent.parent
            end_condition=[]
            go=True
            while gparent is not None and parent!=starting_node:
                i=gparent.children.index(parent)
                if i==len(gparent.children)-1 :
                    end_condition.append(True)
                else: end_condition.append(False)
                parent=gparent
                gparent=parent.parent
                if parent==starting_node:
                    #end_condition.append(True)
                    break
            end_condition.append(True)
            end_condition.reverse()

            for c in end_condition:
                if not c: prefix+=I+SPACE
                else :prefix+=' '+SPACE
            # for i in range(self.level):
            #     prefix+=I+SPACE

        if starting_node==self:
            leader=''
        else:
            leader=L if is_end_node else T
        name=str(self)
        #name=self.phase+'({})'.format(len(self.children))
        #name=name+'_'+shortGuid(self.guid)+'_'+str(self.typeIndex)
        if self.is_selected:
            #name+=SELECT
            name='▌ '+name
        txt=prefix+leader+name

        if _print:print (txt)
        out_str+=txt+'\n'

        for i in range(len(self.children)):
            child=self.children[i]
            is_end=True if i>=len(self.children)-1 else False
            out_str+=child.tree(is_end_node=is_end,starting_node=starting_node,_print=_print)
        return out_str

    def select(self):
        self.is_selected=True

    def unselect(self):
        self.is_selected=False

    def set_parent(self,parent):
        if parent is None: return
        self.parent=parent
        parent.add_child(self)
        #update children level
        #for c in self.children:
        #    c.level=self.level+1

    def set_children(self,children):
        self.children=children
        #for c in self.children:
        #    c.level=self.level+1

    def add_child(self,child):
        self.children.append(child)
        #child.level=self.level+1

    def delete(self):
        if self.parent is not None:
            self.parent.remove_child(self)
        if self.children:
            for c in self.children:
                c.delete()
        # if rs.IsObject(self.guid):
        #     rs.DeleteObject(self.guid)

    def remove_child(self,child):
        #end father and son relationship
        #fist if statement is import if the child is
        #assigned to another father before deleting
        try:
            index=self.children.index(child)
            del self.children[index]
        except:pass
        pass
def demo():
    A=PhaseObject()
    B=PhaseObject(A,phase='B')
    C=PhaseObject(A,phase='C')
    D=PhaseObject(B,phase='D')
    E=PhaseObject(A,phase='E')
    F=PhaseObject(D,phase='F')

    print(F.root)
    print(A.tree())
    fo=A.find('phase','F')
    print('found form a',fo)
    print('----------------')

    B.delete()
    print(A.tree())


    return A


if __name__ == "__main__":
    demo()
# demo()
