
import Rhino
import rhinoscriptsyntax as rs

path='"~/Documents/Design/component.3dm"'

def importComponent(path):
    imported=rs.Command("-Insert "+path+' Objects Enter 0,0,0 1 0')
    if imported:
        components=rs.LastCreatedObjects()
        polys=[]
        breps=[]
        for comp in components:
            if rs.IsCurve(comp):polys.append(comp)
            if rs.IsBrep(comp):breps.append(comp)
        print ('polys \n',polys)
        print ('breps \n',breps)
        return [breps,polys]

breps,polys=importComponent(path)
print ('polys \n',polys)
print ('breps \n',breps)
