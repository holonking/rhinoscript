
import rhinoscriptsyntax as rs
from RsTools import ShapeGrammarM as sg


SAVEFILENAME='Comp1'
SAVEFOLDER='c:\\frames\\'

try:
    total_steps=sg.ENGINE.step
    print('total steps:{}'.format(total_steps))
    geos=sg.ENGINE.step_geometry
    for g in geos:
        #print(len(g))
        pass
    #capturescreen
    frames=[]
    frames2=[]
    
    for i in range(total_steps):
        frames.append(i)
        frames2.append(total_steps-1-i)
    frames+=frames2
    #for i in range(total_steps):
    for i in range(len(frames)):
        file=SAVEFOLDER+SAVEFILENAME+'_{}.jpg'.format(i)
        rs.EnableRedraw(False)
        sg.ENGINE._hide_all()
        #rs.ShowObjects(sg.ENGINE.step_geometry[i])
        rs.ShowObjects(sg.ENGINE.step_geometry[frames[i]])
        rs.EnableRedraw(True)
        rs.Command('_-ScreenCaptureToFile {}'.format(file))
    
except Exception as e:
    print(e)
    pass