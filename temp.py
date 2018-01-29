class Cursor:
    def __init__(self):
        self.x=0
        self.move_left_signal=[]

    def move_left(self):
        self.x -= 1
        for callback in self.move_left_signal:
            callback(dict(sender=self, x=self.x))

#-------------------
class keyManager:
    def __init__(self):
        self.pressed_left=[]
        self.pressed_right = []

    def pressd_left(self):
        for callback in self.pressd_left:
            callback()

#-------------------

c=Cursor()
em=KeyManager()
em.pressed_left += c.move_left


#CASE ONE
#------------------------
class Cursor:
    def __init__(self):
        self.x = 0
        self.move_left_signal = []

    def move_left(self):
        self.x -= 1
        for callback in self.move_left_signal:
            callback()


# -------------------
class EventManager:
    def __init__(self):
        self.key_pressed_signal = {}
        #为每一个key创建一个signal (就是个list of callbacks)
        for k in ['left','right','',.......] :
            self.key_pressed_signal[k]=[]

    def on_key_pressed(self,key):
        for callback in self.key_pressed_sigal[key]:
            callback()

# -------------------
c = Cursor()
em = EventManager()
em.key_pressed_signal['left'] += c.move_left

def print_x(param):
    print(param['x'])
c.move_left_signal+=print_x()
# ------------------------


#CASE TWO
#------------------------
class Cursor:
    def __init__(self):
        self.x = 0
        self.move_left_signal = []

    def move_left(self):
        self.x -= 1
        for callback in self.move_left_signal:
            callback(dict(sender=self, x=self.x))


# -------------------
class EventManager:
    def __init__(self):
        self.key_pressed_signal = []

    def on_key_pressed(self,key):
        for callback in self.key_pressed_sigal[key]:
            callback({'key':key})
# -------------------
class Mapper:
    def __init__(self):
        self.mapping={}

    def map(self,callback,key):
        if not key in self.mapping:
            self.mapping[key]=[]
        self.map[key] += callback
    def key_press_callback(param):
        for callback in self.mapping[param['key']]:
            callback()
# -------------------
c = Cursor()
em = EventManager()
mp=Mapper()
mp.map(c.move_left,'left')
em.key_pressed_signal+= mp.key_press_callback


def print_x(param):
    print(param['x'])
c.move_left_signal+=print_x()
# ------------------------


