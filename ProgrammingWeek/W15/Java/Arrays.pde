void setup() {
    int[] a = { 5, 9, 2 };

    int i = 0;
    while (i < a.length) {
        print(a[i]);
        i = i + 1;
    }
    println();

    i = 0;
    while (i < a.length) {
        println(a[i]);
        i = i + 1;
    }

    for (int j = 0; j < a.length; j = j + 1) {
        println(a[j]);
    }

    for (int x : a) {
        println(x);
    }

    int[] b = new int[5];
    b[0] = 2;
    b[1] = 7;
    b[3] = 8;
    println(b);
}
