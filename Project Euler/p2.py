c = 1
p = 1
sum = 0
while c <= 4000000:
    if c %2 == 0:
        sum += c
    a = c
    c = p + c
    p = a
print(sum)
