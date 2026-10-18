class Balloon:
    def __init__(self, x, y, r):
        self.x = x
        self.y = y
        self.r = r

    def show(self):
        line(self.x, self.y, self.x, self.y + 100)
        ellipse(self.x, self.y, self.r, self.r)

    def move(self):
        if self.y > width / 2:
            self.y = self.y - 2
        else:
            self.y = self.y - 4


balloons = []


def setup():
    size(1000, 1000)
    x_coords = [100, 200, 400, 500, 600]
    y_coords = [900, 850, 600, 700, 950]

    i = 0
    while i < len(x_coords):
        balloons.append(Balloon(x_coords[i], y_coords[i], 50))
        i = i + 1


def draw():
    background(255)
    i = 0
    while i < len(balloons):
        balloons[i].show()
        balloons[i].move()
        i = i + 1
