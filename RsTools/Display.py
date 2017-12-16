import Rhino
from Rhino.Display import DisplayConduit, DrawEventArgs
from Rhino.Geometry import Point2d


class TextConduit(DisplayConduit):
    def __init__(self):
        self.text='test string'
        self.color=(0,0,0)
        self.enabled=True
        self.pos=Point2d(10,10)
        self.height=50

    def set_text(self,text):
        self.text=text
    def DrawOverlay(self, e):
        e.Display.Draw2dText(self.text, self.color,
                             self.pos, self.height)

