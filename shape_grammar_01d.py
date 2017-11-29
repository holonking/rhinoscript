import rhinoscriptsyntax as rs
import RsTools.ShapeGrammar as sg
reload(sg)
eg=sg.ENGINE


rs.EnableRedraw(False)

eg.clear()
eg.add_name('start')


eg.divide('start',[0.35,0.3,0.35],['flank','core'],direction=1,delete_input=False)
eg.copy('core','flow')
eg.divide('core',[0.2,0.8],['garden','core'],direction=0)
eg.scale('garden',[1,1,0.6])

eg.scale('flow',[0.8,1,0.5],centered=False)
eg.move('flow',[-1/4,0,1.1])

#details
eg.divide('flow',[0.1,0.8,0.1],['side','flow'],direction=1)
eg.scale('side',[1.2,1,1.2],centered=True)
eg.move('side',[0,0,-0.05])

#levels
eg.divide('garden',[2,5,'r'],['garden','trash'],direction=2,ratio_mode=False)
eg.scale('garden',[2,1.2,1],centered=True)
eg.delete_name('trash')

eg.rename('core','main')
eg.rename('flank','main')

eg.divide('main',[3.5,'r'],['level_A'],ratio_mode=False, direction=2,)
eg.divide('flow',[6,'r'],['level_B'], ratio_mode=False,direction=2,)



rs.EnableRedraw(True)
