
class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        # super(AttrDict, self).__init__(*args, **kwargs)
        super(dict, self).__init__(*args, **kwargs)
        self.__dict__ = self

class PolyAD(dict):
    def __init__(self, *args, **kwargs):
        super(PolyAD, self).__init__(*args, **kwargs)
        self.__dict__ = self
        self.points = []
        self.directions = []
        self.normals = []
        self.perpFrames = []

def short_guid(guid):
    if guid is None:
        return 'None'
    guid = str(guid)
    txt = str(guid[:2]) + str(guid[-2:])
    return '[' + txt + ']'