a = [5, 9, 2]

i = 0
while i < len(a):
    print(a[i])
    i = i + 1

sum = 0
i = 0
while i < len(a):
    sum = sum + a[i]
    i = i + 1
print("sum =", sum)

print("average =", sum / len(a))

max = a[0]
i = 1            
while i < len(a):
    if max < a[i]:
        max = a[i]
    i = i + 1
print("max =", max)

def is_sorted(a):
    i = 0
    while i < len(a) - 1:      
        if a[i] > a[i + 1]:     
            return False
        i = i + 1
    return True


print(is_sorted([5, 9, 2]))   
print(is_sorted([2, 5, 9]))   


a[0] = 7
print(a)   
