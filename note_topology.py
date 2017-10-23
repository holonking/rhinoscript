
from Deploy_BaseTypes_For_Annotation import *



def block(_print=False):
    if _print:
        print('\nblock\n')
    data=PhaseObject(phase='block')
    if _print:
        sides=PhaseObject(data,phase='sides (6)')
    if _print:
        print(data.tree())
    return data

def subtractive_block(_print=False):
    if _print:
        print('\nsubtractive block\n')
    data=PhaseObject(phase='subtractive_block')
    if _print:
        sides=PhaseObject(data,phase='sides (6)')
    if _print:
        print(data.tree())
    return data

def simple_cube():
    print('\nsimple block\n')
    data=PhaseObject(phase='model (1)')
    sides=PhaseObject(data,phase='sides (6)')
    #for i in range(6):
    #    side=PhaseObject(sides,phase='srf_'+str(i))

    print(data.tree())

def oriented_cube():
    print('\noriented block\n')
    data=PhaseObject(phase='model (1)')
    sides=PhaseObject(data,phase='sides (6)')
    for direction in ['E','S','W','N','Top','Bottom']:
        side=PhaseObject(sides,phase='srf_'+direction)
    print(data.tree())


def mono_building():
    print('\nmonolithic building\n')
    data=PhaseObject(phase='model (2)')
    sides=PhaseObject(data,phase='wall (4)')
    for i in range(4):
        side=PhaseObject(sides,phase='wall_type_1')
    top=PhaseObject(data,phase='roof (1)')
    print(data.tree())

def seagram_building(_print=True):
    print('\nseagram building\n')
    data=PhaseObject(phase='model (3)')
    sides=PhaseObject(data,phase='side_wall (2)')
    fronts=PhaseObject(data,phase='front_wall (2)')
    for i in range(2):
        side=PhaseObject(sides,phase='curtain_wall_stone')
    for i in range(2):
        side=PhaseObject(fronts,phase='curtain_wall_glass')
    top=PhaseObject(data,phase='roof (1)')
    if _print:
        print(data.tree())
    return data

def apartment():
    print('\nsingle loaded apt\n')
    data=PhaseObject(phase='model (4)')
    sides=PhaseObject(data,phase='side_wall (2)')
    front=PhaseObject(data,phase='front_side (1)')
    back=PhaseObject(data,phase='back_side (1)')
    for i in range(2):
        side=PhaseObject(sides,phase='solid_wall')
    PhaseObject(front,phase='balcony_wall')
    PhaseObject(back,phase='corridor')
    top=PhaseObject(data,phase='roof (1)')
    print(data.tree())

def seagram_combo():
    block1=seagram_building(False)
    block2=seagram_building(False)

    block1.add_child(block2)
    print(block1.tree())

def massing1():
    print('\nmodel (3)\n')
    building=PhaseObject(phase='Parkroyal hotel')
    tower=PhaseObject(building,phase='tower (1)')
    void=PhaseObject(building,phase='void (1)')
    podium=PhaseObject(building,phase='podium (2)')

    m1=PhaseObject(tower,phase='block (4)')
    m1.add_child(subtractive_block())
    m1.add_child(subtractive_block())
    m1.add_child(block())
    m1.add_child(block())

    PhaseObject(void,phase='block')
    PhaseObject(podium,phase='block')
    PhaseObject(podium,phase='block')

    print(building.tree())


if __name__ =='__main__':
    simple_cube()
    oriented_cube()
    mono_building()
    seagram_building()
    apartment()
    massing1()
