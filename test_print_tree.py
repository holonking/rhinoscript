# T='├'
# I='│'
# L='└'
# D='─'

SPACE='   '
import os

class Node:
    def __init__(self,name='Node',parent=None,children=[],level=0):
        self.name=name
        self.parent=None
        self.children=[]

        #Should not set level manually!
        self.level=level

        if parent is not None:
            self.set_parent(parent)
        if children is not None:
            if children is list:
                if len(children>0):
                    self.set_children(children)
    def print_node(self,is_end_node=True,starting_node=None):
        prefix=''
        parent=self.parent
        if parent is not None and starting_node is not None:
            gparent=parent.parent
            end_condition=[]
            while gparent is not None:
                if parent==starting_node:break
                i=gparent.children.index(parent)
                if i==len(gparent.children)-1:
                    end_condition.append(True)
                else: end_condition.append(False)
                parent=gparent
                gparent=parent.parent
            end_condition.append(True)
            end_condition.reverse()

            for c in end_condition:
                if not c: prefix+=I+SPACE
                else :prefix+=' '+SPACE
            # for i in range(self.level):
            #     prefix+=I+SPACE


        leader=L if is_end_node else T
        txt=prefix+leader+self.name
        print (txt)
        for i in range(len(self.children)):
            child=self.children[i]
            is_end=True if i>=len(self.children)-1 else False
            child.print_node(is_end_node=is_end,strating_node=starting_node)



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
G=Node('Node_G',parent=C)


A.print_node()
