from RsTools import ShapeGrammarM as sg
import rhinoscriptsyntax as rs

try:
    #sg.ENGINE.delete_imported_components()
    objs=sg.ENGINE.get_by_name('terminal')
    for o in sg.EN:
        print o.name
        o.unstage()
    
except Exception as e:
    print(e)