a = [5, 9, 2]
i = 0
while i < len(a):
    print(a[i])
    i = i + 1

a[0] = 7
print(a)

s = "Hello"
print(s)

i = 0
while i < len(s):
    print(s[i])
    i = i + 1

print("Hello\nWorld")
print("Python\tProgramming")
print("He said \"Hello\"")

s = "Hello"
t = "Joe"
print(s + t)

s = "Hello"
t = ""
i = 0
while i < len(s):
    t = t + str(i)
    i = i + 1
print(t)

s = "Hello"
t = ""
i = 0
while i < len(s):
    t = t + str(i) + "\t" + s[i] + "\n"
    i = i + 1
print(t)

s = "Hello"
try:
    s[0] = "J"
except TypeError as e:
    print(e)

s = "Hello"
s = "J" + s[4] + s[1]
print(s)

s = "3"
print(s.isalnum())
