def print_all(a):
    i = 0
    while i < len(a):
        print(a[i])
        i = i + 1


def add_all(a, x):
    i = 0
    while i < len(a):
        a[i] = a[i] + x
        i = i + 1


a = [5, 9, 2]
print_all(a)

b = [6, 1, 8]
print_all(b)

a = [5, 9, 2]
add_all(a, 3)
print_all(a)

b = [6, 1, 8]
add_all(b, 2)
print_all(b)
