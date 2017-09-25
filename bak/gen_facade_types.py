import Rhino
import rhinoscriptsyntax as rs
import cPickle as pkl
import rsTools
reload(rsTools)
from rsTools import *

facadeType1=AttrDict()
facadeType1.widths=[600,1500]
facadeType1.heights=[300,600]
facadeType1.pattern=[
            [0,1],
            [1,0]
            ]

facadeType2=AttrDict()
facadeType2.widths=[1500,1500,600]
facadeType2.heights=[4200,-1]
facadeType2.pattern=[
            [2,2,0],
            [1,1,0]
            ]

facadeType3=AttrDict()
facadeType3.widths=[900,900,900,900]
facadeType3.heights=[3000,3000]
facadeType3.pattern=[
            [3,3,1,3],
            [1,3,3,3]
            ]

facadeType4=AttrDict()
facadeType4.widths=[1500]
facadeType4.heights=[6000]
facadeType4.pattern=[
            [3]
            ]
facadeType5=AttrDict()
facadeType5.widths=[1500]
facadeType5.heights=[6000]
facadeType5.pattern=[
            [3]
            ]

facadeTypes=[facadeType1,facadeType2,facadeType3,facadeType4,facadeType5]
counter=0
for ft in facadeTypes:
    filename='./FacadePatterns/facadeType_'+str(counter)+'.facade'
    counter+=1
    with open(filename,'wb') as fp:
        pkl.dump(ft,fp)
