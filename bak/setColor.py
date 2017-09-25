
import rhinoscriptsyntax as rs

objs=rs.ObjectsByLayer('GENTYPESRF')
for o in objs:
    c=rs.ObjectColor(o,(255,0,0))
    print(c)
