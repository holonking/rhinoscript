import clr
clr.AddReference('IronPython.Wpf')
import wpf
import System
import System.Windows.Controls as ws
import System.Drawing as wd
from System.Drawing import Size
from System.Windows.Shapes import Line, Rectangle
from System.Windows.Media import SolidColorBrush, Colors
import Rhino

class NameButton(ws.Button):
    def __init__(self,name,canvas=None,position=(0,0),font_size=8):
        self.Content=name
        self.FontSize=font_size
        self._position=position
        self.canvas=canvas

        if canvas:
            canvas.Children.Add(self)
            if position:
                self.position=position
    @property
    def position(self):
        return self._position
    @position.setter
    def position(self,ipos):
        self._position=ipos
        if self.canvas:
            self.SetValue(self.canvas.LeftProperty,float(ipos[0]))
            self.SetValue(self.canvas.TopProperty,float(ipos[1]))
            

class RUI(ws.Canvas):
    def __init__(self):
        super(RUI,self).__init__()
        self.Width=2400
        self.Height=2400
        self.Background = SolidColorBrush(Colors.Beige);
        pass

def rect(w,h,widget):
    rect=Rectangle()
    rect.Fill=SolidColorBrush(Colors.Red)
    rect.Width=w
    rect.Height=h
    rect.SetValue(widget.LeftProperty,10.0)
    rect.SetValue(widget.TopProperty,50.0)
    widget.Children.Add(rect)
    
    
def line(x1, y1, x2, y2, widget):
    line = Line()
    line.Stroke=SolidColorBrush(Colors.Blue)
    line.X1 = float(x1)
    line.X2 = float(x2)
    line.Y1 = float(y1)
    line.Y2 = float(y2)
    widget.Children.Add(line)
    
def main():
    window = System.Windows.Window()
    sv = ws.ScrollViewer()
    
    layout=System.Windows.Controls.StackPanel()
    layout.Orientation=ws.Orientation.Vertical
    
    sv.Content=layout
    window.Content=sv
    window.Width=200
    window.Height=300
    
    rui=RUI()
    #rui.Width=window.Width
    #rui.Height=window.Height
    layout.Children.Add(rui)
    
    bt1=NameButton('asd',rui,(100,100))
    bt2=NameButton('gdfa',rui,(150,100))
    bt1.Content='fffff'
    line(0,0,100,100,rui)
    rui.Children.Remove(bt2)
    rui.Children.Add(bt2)
    #rect(100,50,rui)
    return window
    
    
if __name__ == '__main__':
    window=main()
    System.Windows.Interop.WindowInteropHelper(window).Owner = Rhino.RhinoApp.MainWindowHandle()
    window.Show()
    