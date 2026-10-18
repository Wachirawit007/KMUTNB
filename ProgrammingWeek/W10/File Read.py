with open("example.txt", "w") as file:
    file.write("5\n")
    file.write("2\n")
    file.write("7\n")

file = open("example.txt", "r")
content = file.read()
print(content)
file.close()

with open("example.txt", "r") as file:
    content = file.read()
    print(content)

with open("example.txt", "r") as f:
    line = f.readline()
    while line:
        print(line)
        line = f.readline()

with open("example.txt", "r") as file:
    for line in file:
        print(line)

a = []
with open("example.txt", "r") as file:
    for line in file:
        num = int(line)
        a.append(num)
print(a)
