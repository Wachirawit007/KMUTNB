with open("output.txt", "w") as file:
    file.write("Hello Python\n")
    file.write("Welcome to Thailand\n")

with open("output.txt", "a") as file:
    file.write("ECE\n")
    file.write("KMUTNB\n")

try:
    with open("example.txt", "r") as file:
        for line in file:
            print(line)
except FileNotFoundError:
    print("Error: example.txt is not found")
