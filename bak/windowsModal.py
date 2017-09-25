import System.Windows.Forms

class HelloWorldForm(System.Windows.Forms.Form):
    def __init__(self):
        self.Text = 'Hello World'
        self.Name = 'Hello World'

form = HelloWorldForm()
form.ShowDialog()
