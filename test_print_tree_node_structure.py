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
R1=Node('Rule_R1',parent=A)
B=Node('Node_B',parent=A)

R2=Node('Rule_R2',parent=B)
C=Node('Node_C',parent=B)
D=Node('Node_D',parent=B)

R3=Node('Rule_R3',parent=C)
D1=Node('Node_D1',parent=C)
E=Node('Node_E',parent=C)

R4=Node('Rule_R4',parent=D)
F=Node('Node_F',parent=D)

A.tree()


R1=Node('Rule_R1')
R1I=Node('Inputs :[A]',parent=R1)
R1O=Node('Outputs:[B]',parent=R1)

R2=Node('Rule_R2',parent=R1)
R2I=Node('Inputs :[B]',parent=R2)
R2O=Node('Outputs:[C,D]',parent=R2)

R3=Node('Rule_R3',parent=R2)
R3I=Node('Inputs :[C]',parent=R3)
R3O=Node('Outputs:[D,E]',parent=R3)

R4=Node('Rule_R4',parent=R2)
R4I=Node('Inputs :[D]',parent=R2)
R4O=Node('Outputs:[F]',parent=R2)

print('')
R1.tree()

A=Node('Node_A')
R1=Node('Rule_R1',parent=A)
B=Node('Node_B',parent=R1)
R2=Node('Rule_R2',parent=B)
C=Node('Node_C',parent=R2)
D=Node('Node_D',parent=R2)
R3=Node('Rule_R3',parent=C)
D1=Node('Node_D1',parent=R3)
E=Node('Node_E',parent=R3)
R4=Node('Rule_R4',parent=D)
F=Node('Node_F',parent=R4)
A.tree()