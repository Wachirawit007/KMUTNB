int x = 100;

void draw_balloon(int x, int y) {
    ellipse(x, y, 100, 100);
    line(x, y + 50, x, y + 200);
}

void setup() {
    size(500, 500);
}

void draw() {
    draw_balloon(x, 200);
    x = x + 10;
    if (x > width) {
        x = 100;
    }
}
