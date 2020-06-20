highest_p = 0
for i in range(100, 1000):
    for n in range(i, 1000):
        p = str(n*i)
        p2 = p[::-1]
        if p == p2 and int(p) > highest_p:
            highest_p = int(p)
print(highest_p)
