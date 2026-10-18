n = 10
x = []   
y = []   
s = []   


def draw_circle(cx, cy, d):
    ellipse(cx, cy, d, d)


def setup():
    size(1000, 1000)
    i = 0
    while i < n:
        x.append(random(100, 900))
        y.append(random(100, 500))
        s.append(random(1, 5))       
        i = i + 1


def draw():
    background(255)
    i = 0
    while i < n:
        draw_circle(x[i], y[i], 20)
        y[i] = y[i] + s[i]           
        i = i + 1

id = [1, 7, 199]
health = [100, 70, 80]
score = [50, 120, 90]

product = ["Apple", "Banana", "Orange"]
price = [1.20, 0.80, 1.50]
stock = [30, 50, 20]
