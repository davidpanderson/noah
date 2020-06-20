v = 2
n = 600851475143
while n > 1:
    if n%v == 0:
        n /= v
    else:
        v += 1
print(v)
