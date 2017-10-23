import rhinoscriptsyntax as rs

def vectorlistEqual(arr1,arr2):
    if len(arr1)!=len(arr2):return False
    for p1,p2 in zip(arr1,arr2):
        print(p1==p2,p1,p2)
 
        
    
    
srf1=rs.GetObject('srf1')
srf2=rs.GetObject('srf2')


pts0=rs.SurfaceEditPoints(srf1)
pts1=rs.SurfaceEditPoints(srf2)

print(pts0==pts1)
vectorlistEqual(pts0,pts1)