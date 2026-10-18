class EsBalloon(Balloon):
    # EsBalloon is a sublcass of Balloon
    # for expanding and shinking balloon

    def __init__(self, x, y, r):
        # define the constuctor
        super().__init__(x, y, r)
        # call the constuctor of the superclass
        self.change = 1
        # add a new attribute

    def expand_shrink(self):
        self.r = self.r + self.change

        if self.r >= 60:
            self.change = -1
        elif self.r <= 30:
            self.change = 1

    def move(self):  # override move() in the superclass
        super().move()  # call the superclass method
        self.expand_shrink()  # call its own method


def setup():
    size(1000, 1000)
    x_coords = [100, 200, 400, 500, 600]
    y_coords = [900, 850, 600, 700, 950]

    i = 0
    while i < len(x_coords):
        balloons.append(EsBalloon(x_coords[i], y_coords[i], 50))
        i = i + 1


def draw():
    background(255)
    i = 0
    while i < len(balloons):
        balloons[i].show()
        balloons[i].move()
        # balloons[i].expand_shrink()  # include it in move()?
        i = i + 1
