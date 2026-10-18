class Balloon {
    int x;
    int y;
    int r;

    Balloon(int x, int y, int r) {
        this.x = x;
        this.y = y;
        this.r = r;
    }

    void show() {
        line(this.x, this.y, this.x, this.y + 100);
        ellipse(this.x, this.y, this.r, this.r);
    }

    void move() {
        this.y = this.y - 2;
    }
}

Balloon t;
Balloon[] b;

void setup() {
    size(500, 500);

    t = new Balloon(200, 200, 70);

    b = new Balloon[5];
    for (int i = 0; i < b.length; i = i + 1) {
        int x = (int) random(50, 450);
        int y = (int) random(50, 500);
        int r = (int) random(30, 80);
        b[i] = new Balloon(x, y, r);
    }
}

void draw() {
    background(255);

    t.show();
    t.move();

    for (int i = 0; i < b.length; i = i + 1) {
        b[i].show();
        b[i].move();
    }
}
