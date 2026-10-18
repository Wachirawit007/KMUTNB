def print_all(a):
    i = 0
    while i < len(a):
        print(a[i])
        i = i + 1


def print_2D(m):
    i = 0
    while i < len(m):
        print_all(m[i])
        i = i + 1


def print_2Dn(m):
    i = 0
    while i < len(m):
        j = 0
        while j < len(m[i]):
            print(m[i][j])
            j = j + 1
        i = i + 1


def sum_2Dn(m):
    sum = 0
    i = 0
    while i < len(m):
        j = 0
        while j < len(m[i]):
            sum = sum + m[i][j]
            j = j + 1
        i = i + 1
    return sum


def count_2Dn(m, x):
    count = 0
    i = 0
    while i < len(m):
        j = 0
        while j < len(m[i]):
            if m[i][j] == x:
                count = count + 1
            j = j + 1
        i = i + 1
    return count


a = [3, 8, 2]
m = [[5, 7, 9], [2, 4, 6], [8, 3, 1]]

m = [[5, 7, 9], \
     [2, 4, 6], \
     [8, 3, 1]]

print(m[0][0])
print(m[0][1])
print(m[1][0])

print(m[1][1])
print(m[2][2])
print(m[1][2])

m[1][2] = 7
m[2][2] = 5

print_all(m[1])

print_all(m[0])
print_all(m[1])
print_all(m[2])

print_2D(m)
print_2Dn(m)

m = [[5, 7, 9], [2, 4, 6], [8, 3, 1]]
print(sum_2Dn(m))
print(count_2Dn(m, 3))
