import rhinoscriptsyntax as rs
import RsTools.ShapeGrammar as sg
reload(sg)
eg=sg.ENGINE


rs.EnableRedraw(False)

eg.clear()
eg.add_name('start')

def rule1(name):
    eg.divide(name,[0.6,0.4],[name+'body',name+'output'],direction=2)
    eg.divide(name+'body',[0.2,0.6,0.2],[name+'A',name+'B'],direction=0)
    eg.scale(name+'A',[1,0.8,1],centered=True)
    eg.scale(name+'output',[1,0.8,1],centered=True)

eg.copy('start','A')
name=eg.recursion(rule1,3,'A')

eg.scale(name,[0.6,1,1],centered=True)
eg.divide(None,[3.5,'r'],direction=2,ratio_mode=False)

#eg.move('core',[1,0,0])

rs.EnableRedraw(True)
