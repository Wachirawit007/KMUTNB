n = 5
sum = 0
count = 1
while count <= n:
    sum = sum + count
    count = count + 1
print("Sum =", sum)


def sum_1_to_n(n):
    sum = 0
    count = 1
    while count <= n:
        sum = sum + count
        count = count + 1
    return sum

def sum_m_to_n(m, n):
    sum = 0
    count = m
    while count <= n:
        sum = sum + count
        count = count + 1
    return sum

def main():
    n = 5
    print("Sum from 1 to", n, "=", sum_1_to_n(n))
    n = 10
    print("Sum from 1 to", n, "=", sum_1_to_n(n))
    print("Sum from 3 to 6 =", sum_m_to_n(3, 6))


if __name__ == "__main__":
    main()
