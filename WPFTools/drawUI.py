import clr
clr.AddReference('IronPython.Wpf')
import wpf
import System
import System.Windows.Controls as ws
import System.Drawing as wd
from System.Drawing import Size, Point
from System.Windows.Shapes import Line
import Rhino


def line(x1, y1, x2, y2, widget, color=None, line_width=1):
    line = Line()
    line.X1 = x1
    line.X2 = x2
    line.Y1 = y1
    line.Y2 = y2
    line.StrokeThickness = line_width
    # TODO: line.Stroke=xxxx

    widget.Children.Add(line)

def line2(p1,p2,widget, color=None, line_width=1):
    line(p1.X, p1.Y, p2.X, p2.Y, widget, color, line_width)

