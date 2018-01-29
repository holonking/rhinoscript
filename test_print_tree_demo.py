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

RS=Node('(0)start')
RSO=Node('Outputs:[com]',parent=RS)
R1=Node('(1)divide_mx(0.35)',parent=RSO)
R1I=Node('Inputs :[com]',parent=R1)
R1O=Node('Outputs:[flank,mid]',parent=R1)

R2=Node('(02)divide_x(0.5，0.5)',parent=R1)
R2I=Node('Inputs :[flank]',parent=R2)
R2O=Node('Outputs:[A,B]',parent=R2)

R3=Node('(3)scale_y(1.2)',parent=R2)
R3I=Node('Inputs :[A]',parent=R3)
R3O=Node('Outputs:[A]',parent=R3)

R4=Node('(4)scale_x(1.1)',parent=R3)
R4I=Node('Inputs :[A]',parent=R4)
R34O=Node('Outputs:[A]',parent=R4)

R5=Node('(5)divide_y(0.3,0.4,0.3)',parent=R4)
R5I=Node('Inputs :[A]',parent=R5)
R5O=Node('Outputs:[corner,ent]',parent=R5)

R6=Node('(6)scale_z(1.1)',parent=R5)
R6I=Node('Inputs :[corner]',parent=R6)
R6O=Node('Outputs:[corner]',parent=R6)

R7=Node('(7)scale_y(1.2)',parent=R1)
R7I=Node('Inputs :[mid]',parent=R7)
R7O=Node('Outputs:[mid]',parent=R7)

R8=Node('(8)scale_z(1.1)',parent=R7)
R8I=Node('Inputs :[mid]',parent=R8)
R8O=Node('Outputs:[mid]',parent=R8)

R9=Node('(9)divide_z(5,r)',parent=R8)
R9I=Node('Inputs :[mid]',parent=R9)
R9O=Node('Outputs:[m_l1,m_main]',parent=R9)

R10=Node('(10)divide_z(5,r)',parent=R2)
R10I=Node('Inputs :[B]',parent=R10)
R10O=Node('Outputs:[f_l1,f_main]',parent=R10)

R11=Node('(11)divide_z(5,r)',parent=R5)
R11I=Node('Inputs :[Ent]',parent=R11)
R11O=Node('Outputs:[e_l1,e_main]',parent=R11)

R12=Node('(12)scale_x(0.9)',parent=R11)
R12I=Node('Inputs :[emain]',parent=R12)
R12O=Node('Outputs:[e_main]',parent=R12)

R13=Node('(12)scale_x(0.95)',parent=R11)
R13I=Node('Inputs :[e_l1]',parent=R13)
R13O=Node('Outputs:[e_l1]',parent=R13)

R14=Node('(12)scale_y(0.7)',parent=R10)
R14I=Node('Inputs :[f_l1]',parent=R14)
R14O=Node('Outputs:[ef_l1]',parent=R14)


RS.tree()



