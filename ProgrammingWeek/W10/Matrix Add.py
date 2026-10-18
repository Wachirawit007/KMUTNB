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


A = [[1, 2], \
     [3, 4]]
B = [[5, 6], \
     [7, 8]]
print(addm(A, B))
