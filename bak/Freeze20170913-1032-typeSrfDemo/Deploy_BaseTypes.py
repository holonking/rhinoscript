class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        # super(AttrDict, self).__init__(*args, **kwargs)
        super(dict,self).__init__(*args, **kwargs)
        self.__dict__ = self

class PhaseObject(AttrDict):
    def __init__(self, *args, **kwargs):
        super(AttrDict,self).__init__(*args, **kwargs)
        self.guid=-1
        self.downStream=[]
        self.upStream=None
        self.phase=None
        self.needUpdate=False
        self.typeIndex=0
        self.description=''
