void draw_balloon(int x, int y) {
    ellipse(x, y, 100, 100);
    line(x, y + 50, x, y + 200);
}

void setup() {
    size(500, 500);
    int p = Integer.parseInt("70");
    println(p);
}

void draw() {
    int x = (int) random(100, 400);
    draw_balloon(x, 80);
}
