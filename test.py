import rhinoscriptsyntax as rs

srfs=rs.GetObjects('sel srfs')

result=rs.JoinSurfaces(srfs,True)
print ('result is :',result)
