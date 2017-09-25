import System.Windows.Forms

class HelloWorldForm(System.Windows.Forms.Form):
    def __init__(self):
        self.Text = 'Hello World'
        self.Name = 'Hello World'
        self.Closing += self.OnClosingEvent
        System.Windows.Forms.Application.Run(self)
    def OnClosingEvent(self, sender, e):
        self.Close()
        System.Windows.Forms.Application.Exit()

form = HelloWorldForm()
