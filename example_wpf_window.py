import clr
clr.AddReference('IronPython.Wpf')
import wpf
import System
import System.Windows.Controls as ws
import System.Drawing as wd
from System.Drawing import Size
import Rhino

class RuleUI(ws.StackPanel):
    def __init__(self,name,parent):
        super(RuleUI,self).__init__()
        self._parent=parent
        self._parent.Children.Add(self)
        self.Width=self._parent.Width
        self.Height=20
        self.Margin=System.Windows.Thickness(0)
        self.Orientation=ws.Orientation.Horizontal
        
        lb=ws.Label()
        lb.Content=name
        lb.Padding=System.Windows.Thickness(0)
        lb.Height=20
        self.lb=lb
        self.Children.Add(lb)
        
        self.bt_sel = ws.Button()
        self.bt_sel.Content='Sel'
        #self.bt_sel.Width=30
        self.bt_attr = ws.Button()
        self.bt_attr.Content='Attr'
        #self.bt_attr.Width=30
        self.Children.Add(self.bt_sel)
        self.Children.Add(self.bt_attr)
        
    def set_text(self,text):
        self.lb.Content = text
        

window = System.Windows.Window()
sv = ws.ScrollViewer()


layout=System.Windows.Controls.StackPanel()
layout.Orientation=ws.Orientation.Vertical

sv.Content=layout
window.Content=sv

print(layout.Orientation)
window.Width=200
window.Height=300



def add_button(control,text=None):
    if text==None:
        text=str(len(control.Children))
    button=ws.Button()
    button.Height=20
    button.Content=text
    button.Width=control.Width
    control.AddChild(button)
    def on_click(sender, e):
        try:
            text=str(len(control.Children))
            text='script number {}'.format(text)
            RuleUI(text,control)
        except Exception as e:
            print(e)
    button.Click+=on_click

add_button(layout,'+')


System.Windows.Interop.WindowInteropHelper(window).Owner = Rhino.RhinoApp.MainWindowHandle()
window.Show()