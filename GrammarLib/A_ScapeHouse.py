from GrammarLib import Grammar
import RsTools.ShapeGrammarM as sg

class A_ScapeHouse(Grammar):
    def run(self,name,out_names,prefix='ddfgdfgdfgsdasd'):
        s = prefix
        self.step_text='{} -> ScapeHouse -> {}'

        ys=[1.5,0.9,1.5]
        zs=[1.5,0.5,1]

        sg.divide_x(name,[3.1,3,3.2],[s+'A',s+'B',s+'C'])
        sg.scale_y(s + 'A', ys[0], sg.Align.W)
        sg.scale_y(s + 'B', ys[1], sg.Align.W)
        sg.scale_y(s + 'C', ys[2], sg.Align.W)

        sg.scale_z(s + 'A', zs[0], sg.Align.W)
        sg.scale_z(s + 'B', zs[1], sg.Align.W)
        sg.scale_z(s + 'C', zs[2], sg.Align.W)



