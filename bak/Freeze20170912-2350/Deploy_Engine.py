import Rhino
import cPickle as pkl
import rhinoscriptsyntax as rs

import rsTools
reload(rsTools)
from rsTools import *

import Deploy_BaseTypes
reload(Deploy_BaseTypes)
from Deploy_BaseTypes import *

PATH_PATTERN='./FacadePatterns'
PHASES=['BLOCK','MASSING','TYPESRF','TYPEMESH']

SRFTYPECOLORS=[
            (60,160,208),
            (255,89,25),
            (242,192,120),
            (250,237,202),
            (193,219,179),
            (126,188,137),
            (8,111,161)
            ]

MESHTYPECOLORS=[(0,102,204),
            (51,153,255),
            (153,204,255),
            (255,204,204),
            (255,102,102),
            (153,0,0)]

LAYERNAMES=['GENBLOCK','GENMASSING','GENTYPESRF',
            'GENTYPEMESH','GENCOMPONENT']

class Engine():
    def __init__(self):

        #load data
        #self.data=self.loadData()
        self.data=None
        print('loaded data:',self.data)
        if self.data is None:
            self.importSrfTypesFromScene()
            self.reset_GENTYPESRF_color()
        #print('imported data:',self.data)
        print('imported data:')
        for o in self.data:
            print(o.guid)

        #load facade types
        self.loadFacadeTypes()
        print('loaded facade types:',self.facadeTypes)

        #selection
        self.selectedItems=[]

        #layers
        self.initLayers()

    def load(self):
        self.data=self.loadData()
    def loadData(self):
        #serialize the dic from a txt file
        try:
            with open('Data','rb') as fp:
                d1=pkl.load(fp)
            return d1
        except: return None
    def save(self):
        self.saveData(self.data)
    def saveData(self,data):
        try:
            filename='Data'
            with open(filename,'wb') as fp:
                pkl.dump(data,fp)
            print('engine data saved sucess')
        except:
            print('save faile failed')

    #selection management
    def clearSelections(self):
        self.selectedItems=[]
    def addToSelection(self,items):
        for i in items:
            self.selectedItems.append(i)
    def setSelection(self,items):
        self.selectedItems=items

    #layer managements
    def initLayers(self):
        for n in LAYERNAMES:
            rs.AddLayer(n,locked=True)


    def importSrfTypesFromScene(self):

        data=[]
        srfs=rs.ObjectsByLayer('GENTYPESRF')
        for f in srfs:
            po=PhaseObject()
            po.guid=f
            po.phase='TYPESRF'
            po.typeIndex=int(rs.ObjectName(f))
            po.strTypeDescription=rs.ObjectName(f)
            data.append(po)
        self.data=data

    def loadFacadeTypes(self):
        facadeTypes=[]
        import os
        directory='./FacadePatterns/'
        files=os.listdir(directory)
        for f in files:
            if f.find('.facade')>0:
                filename=directory+f
                with open(filename,'rb') as fp:
                    facadeTypes.append(pkl.load(fp))

        self.facadeTypes=facadeTypes

    def updateFacadeType(self,i,filename):
        directory='./FacadePatterns/'
        filename=directory+filename
        print('file name @ updateFacadeType: ',filename)
        with open(filename,'rb') as fp:
            facade=pkl.load(fp)
        self.facadeTypes[i]=facade
        print('facade type:',i,'is updated to ',filename)
        for t in self.facadeTypes:
            print(t)



    def fixCurrentModel(self):
        #fix srf in current scene
        layer='GENTYPESRF'
        srfs=rs.ObjectsByLayer(layer)
        counter=0
        global SRFTYPECOLORS
        for f in srfs:
            rs.ObjectLayer(f,layer)
            typeindex=int(rs.ObjectName(f))
            index=typeindex%len(SRFTYPECOLORS)
            color=SRFTYPECOLORS[index]
            rs.ObjectColor(f,color)
            counter+=1
    def get_SRFTYPECOLOR(self,index):
        index=index%len(SRFTYPECOLORS)
        return SRFTYPECOLORS[index]
    def get_MESHTYPECOLOR(self,index):
        index=index%len(MESHTYPECOLORS)
        return MESHTYPECOLORS(index)
    def reset_GENTYPESRF_color(self):
        for o in self.data:
            if o.phase=='TYPESRF':
                colorIndex=o.typeIndex%len(SRFTYPECOLORS)
                color=SRFTYPECOLORS[colorIndex]
                rs.ObjectColor(o.guid,color)
    def streamDirection(self,phase1,phase2):
        #determin the direction of phase 2 compares to phase 1
        # -1=upstream, 1=downstream, 0=same phase
        if phase1==phase2:return 0
        i1=PHASES.index(phase1)
        i2=PHASES.index(phase2)
        if i2<i1: return -1
        else: return 1
    def getObjectByGuid(self,guid):
        for o in self.data:
            if o.guid==guid: return o,o.upStream
    def getObject(self,phaseIndex,typeIndex=None):
        selection=[]
        for o in self.data:
            #print('@getObject',o.phase,phaseIndex)
            if o.phase==phaseIndex:
                if typeIndex is None: flag=True
                elif typeIndex==o.typeIndex: flag=True
                else: flag=False
                if flag: selection.append(o)
        return selection


    def getObjectPhaseObject(self,obj,phase):
        #finds the object's up or down stream objects
        phase1=obj.phase
        phase2=phase
        i1=PHASES.index(phase1)
        i2=PHASES.index(phase2)
        direction=self.streamDirection(phase1,phase2)
        selection=[]
        if direction==0: return obj
        # stop=i2+direction
        while not i1==i2:
            i1+=direction
            selection+=obj.downStream
        return selection
    def getPathPattern(self):
        return PATH_PATTERN
