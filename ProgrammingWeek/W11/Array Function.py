a = [5, 9, 2]


def print_all(a):
    i = 0
    while (i < len(a)):
        print(a[i])
        i = i + 1


print_all(a)


m = [[5, 7, 9],
     [2, 4, 6],
     [8, 3, 1]]

print(m[0][0])
print(m[0][1])
print(m[1][0])

m[1][2] = 7
m[2][2] = 5

print_all(m[1])

print_all(m[0])
print_all(m[1])
print_all(m[2])


def print_2D(m):
    i = 0
    while (i < len(m)):
        print_all(m[i])
        i = i + 1


print_2D(m)


def print_2Dn(m):
    i = 0
    while (i < len(m)):
        j = 0
        while (j < len(m[i])):
            print(m[i][j])
            j = j + 1
        i = i + 1


print_2Dn(m)


def sum_2Dn(m):
    sum = 0
    i = 0
    while (i < len(m)):
        j = 0
        while (j < len(m[i])):
            sum = sum + m[i][j]
            j = j + 1
        i = i + 1
    return sum


print(sum_2Dn(m))


def count_2Dn(m, x):
    count = 0
    i = 0
    while (i < len(m)):
        j = 0
        while (j < len(m[i])):
            if (m[i][j] == x):
                count = count + 1
            j = j + 1
        i = i + 1
    return count


print(count_2Dn(m, 5))


def addm(A, B):
    result = []
    i = 0
    while i < len(A):
        row = []
        j = 0
        while j < len(A[i]):
            row.append(A[i][j] + B[i][j])
            j = j + 1
        result.append(row)
        i = i + 1
    return result


A = [[1, 2],
     [3, 4]]

B = [[5, 6],
     [7, 8]]

print(addm(A, B))
