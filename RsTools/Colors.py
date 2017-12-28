COLOR_SET_01 = [(60, 160, 208),
                (255, 89, 25),
                (242, 192, 120),
                (250, 237, 202),
                (193, 219, 179),
                (126, 188, 137),
                (8, 111, 161)
                ]

class ColorWheel():
    def __init__(self, color_set=COLOR_SET_01):
        self.current=0
        self.color_set=color_set
    def get_next(self):
        index=self.current % len(self.color_set)
        self.current += 1
        return self.color_set[index]

