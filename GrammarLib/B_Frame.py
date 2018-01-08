from GrammarLib import Grammar

class B_Frame(Grammar):
    def run(self,name,out_names,width=0.6,depth=1,prefix=''):
        s = prefix
        self.step_text='{} -> B_Frame -> {}'



