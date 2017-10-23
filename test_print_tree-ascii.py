# -*- coding: utf-8 -*-
T='├─'
I='│'
L='└─'
D='─'
SELECT=' █'
SPACE='   '
import os

class Node:
    def __init__(self,name='Node',parent=None,children=[],level=0):
        self.name=name
        self.parent=None
        self.children=[]
        self.is_selected=False
        #Should not set level manually!
        self.level=level

        if parent is not None:
            self.set_parent(parent)
        if children is not None:
            if children is list:
                if len(children>0):
                    self.set_children(children)
    def __str__(self):
        txt='Node:'+self.name+' | children count:'+str(len(self.children))
        return txt
    def tree(self,is_end_node=True,starting_node=None,out_str='',_print=True):
        if starting_node is None:
            starting_node=self
            out_str=''
            prefix=''
        else: prefix=' '+SPACE
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


        leader=L if is_end_node else T
        name=self.name
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
        self.parent=parent
        parent.add_child(self)
        #update children level
        for c in self.children:
            c.level=self.level+1
    def set_children(self,children):
        self.children+=children
        for c in self.children:
            c.level=self.level+1
    def add_child(self,child):
        self.children.append(child)
        child.level=self.level+1

A=Node('Node_A')
B=Node('Node_B',parent=A)
C=Node('Node_C',parent=A)
D=Node('Node_D',parent=B)
E=Node('Node_E',parent=B)
F=Node('Node_F',parent=B)
G=Node('Node_G',parent=D)

G.select()
txt=A.tree()
print(txt)
print(A)
#A.print_node()
