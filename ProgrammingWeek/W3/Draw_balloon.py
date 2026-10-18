# Python Mode for Processing

x = 100                      

def setup():
    size(500, 500)
    frameRate(30)

# ---------- user-defined function (ไม่ return ค่า) ----------
def draw_circle(x, y, r):
    ellipse(x, y, r*2, r*2)  

def draw_balloon(x, y, r):
    draw_circle(x, y, r)     
    line(x, y + r, x, y + r + 150)

# ---------- user-defined function (return ค่า) ----------
def cal_distance(x1, y1, x2, y2):
    diffx = abs(x1 - x2)
    diffy = abs(y1 - y2)
    result = sqrt(diffx*diffx + diffy*diffy)   
    return result

# ---------- draw() ทำงานซ้ำตลอด ----------
def draw():
    global x                 
    background(200)

    draw_balloon(x, 200, 50)
    d = cal_distance(x, 200, mouseX, mouseY)

    
    if mouseX > x:
        line(x, 200, x + d, 200)
    else:
        line(x, 200, x - d, 200)

    x = x + 10               
    if x > width:            
        x = 100
