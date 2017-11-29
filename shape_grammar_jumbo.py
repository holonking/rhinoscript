import rhinoscriptsyntax as rs
import RsTools.ShapeGrammar as sg
reload(sg)
eg=sg.ENGINE


rs.EnableRedraw(False)

eg.clear()
eg.add_name('start')
eg.copy('start','node')

eg.divide('node',[12,'r'],['even','odd'],direction=2,ratio_mode=False)
eg.divide('even',[9,'r'],['A','B','B'],direction=1,ratio_mode=False)
eg.divide('odd' ,[9,'r'],['B','A','A'],direction=1,ratio_mode=False)

eg.scale('B',[1.3,1,1],centered=True)


#eg.move

rs.EnableRedraw(True)
