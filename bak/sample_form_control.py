import System.Windows.Forms as Forms
import System.Drawing as Drawing
from System.Drawing import *
import Rhino
import rhinoscriptsyntax as rs

class HelloWorldForm(Forms.Form):
    def __init__(self):
        self.Text = 'Hello World'
        self.Name = 'Hello World'
        self.Size=Size(150,350)
        self.Closing += self.OnClosingEvent
        self.initUI()


    def OnClosingEvent(self, sender, e):
        print('closing window form, remove handler')

    def initUI(self):
        #UI code
        print('init UI')
        # button1=System.Windows.Forms.Button()
        # button1.Location=System.Drawing.Point(5,10)
        # self.Controls.Add(button1)
        self.SuspendLayout()

        lay=Forms.FlowLayoutPanel()
        lay.FlowDirection=Forms.FlowDirection.LeftToRight
        lay.Location=Point(10,10)
        lay.Size=Size(200,300)
        lay.Text='TopToBottom'
        lay.SuspendLayout()

        tb1=Forms.TextBox()
        tb1.Text='hello'
        tb2=Forms.TextBox()
        tb2.Text='world'

        #tb2.Location=Point(0,20)
        # tb.Location=Drawing.Point(10,10)
        #tb1.Location=Point(10,10)
        lay.Controls.Add(tb1)
        lay.Controls.Add(tb2)

        self.Controls.Add(lay)
        lay.ResumeLayout(False)
        self.ResumeLayout(False)
        # self.Controls.Add(tb)


form = HelloWorldForm()
form.TopMost=True
form.Show()
