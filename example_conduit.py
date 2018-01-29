import Rhino
import System
import time


class myConduit(Rhino.Display.DisplayConduit):
    def __init__(self):
        super(myConduit,self).__init__()
    def PreDrawObjects(self,e):
        try:
            #super().PreDrawObjects(e)
            p1=Rhino.Geometry.Point3d(0,0,0)
            p2=Rhino.Geometry.Point3d(5,2,2)
            color=System.Drawing.Color.Red
            mat=Rhino.Display.DisplayMaterial(color)
            e.Display.DrawArrow(Rhino.Geometry.Line(p1,p2),color)
        except Exception as e:
            print(e)
            time.sleep(0.1)


def main():
    from ShapeGrammar.conduit.monitor import ConduitMonitor
    conduit=myConduit()
    cm=ConduitMonitor(conduit)

if __name__ == '__main__':
    main()