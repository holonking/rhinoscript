import RsTools.ShapeGrammarM as sg

class Grammar:
    def __init__(self, *args, **kwargs):
        self.step_text='please set value to self.step_text'
        sg.ADDSTEPS = False
        sg.enable_print_steps(False)

        self.run()

        sg.ADDSTEPS = True
        sg.enable_print_steps(True)
        sg.ENGINE.add_step(self.step_text)
        pass

    def run(self,*args,**kwargs):
        # override
        pass