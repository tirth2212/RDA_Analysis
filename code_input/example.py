a = 1
b = 2

if a < b:
    c = a + b
    if c > 2:
        b = c - a
        
    else:
        c = b - a
        
else:
    d = a * b

for i in range(2):
    a = a + i
    b = b - i
    break

while b > 0:
    c = c + 1
    b = b - 1
    pass

e = a + b + c
