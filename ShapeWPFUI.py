import clr
clr.AddReference('IronPython.Wpf')
import wpf
import System
import Rhino


class ShapeWindow(System.Windows.Window):
    def __init__(self):
        System.Windows.Interop.WindowInteropHelper(self).Owner = Rhino.RhinoApp.MainWindowHandle()



