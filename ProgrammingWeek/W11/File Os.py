import os

f = open("output.txt", "w")
f.write("Hello, everybody")
f.close()

print(os.getcwd())

print(os.chdir("c:\\home"))
print(os.getcwd())

print(os.listdir())

print(os.path.exists("sample"))
print(os.path.isfile("sample"))
print(os.path.isdir("sample"))

file_size = os.path.getsize("output.txt")
print("File Size is :", file_size, "bytes")
