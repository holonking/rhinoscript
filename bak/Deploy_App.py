import Rhino
import rhinoscriptsyntax as rs

import Deploy_Engine
reload(Deploy_Engine)
from Deploy_Engine import Engine

import Deploy_UI
reload(Deploy_UI)
from Deploy_UI import MainForm

import Deploy_AssignActions
reload(Deploy_AssignActions)
from Deploy_AssignActions import *

engine=Engine()

form = MainForm()
form.TopMost=True

assignAction(form,engine)

form.Show()
