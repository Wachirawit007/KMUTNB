s = "Hello"          
print(s)

i = 0
while i < len(s):
    print(s[i])
    i = i + 1

i = 0
while i < len(s):
    print(ord(s[i]))   
    i = i + 1

print(ord("a"))   
print(ord('a'))   
print(ord('A'))   
print(ord('0'))   
print(chr(97))    
print(chr(65))    

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
    t = t + str(i) + "\t" + s[i] + "\n"   
    i = i + 1
print(t)


s = "Hello"
s = "J" + s[4] + s[1]   
print(s)                

s = "Hello"
print(s.upper())       
print(s.lower())       
print("A".isalpha())   
print("3".isalpha())   
print("3".isdigit())   
print("3".isalnum())   

def draw():
    fill(0)                      
    textSize(100)                
    text("ABC", mouseX, mouseY)
