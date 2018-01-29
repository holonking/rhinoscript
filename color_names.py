
import rhinoscriptsyntax as rs
from RsTools import ShapeGrammarM as sg
from RsTools.Colors import ColorWheel 



try:
    eg=sg.ENGINE

    colors={}
    wheel=ColorWheel()
    rs.EnableRedraw(False)
    for i in range(len(eg.data)):
        o=sg.ENGINE.data[i]
        name=o.name
        if name not in colors:
            colors[name]=wheel.get_next()
        
        try:
            rs.ObjectColor(o.guid,colors[o.name])
        except:
            pass
    rs.EnableRedraw(True)
except Exception as e:
    rs.EnableRedraw(True)
    print(e)
    pass