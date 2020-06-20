n = 20
while True:
    found = False
    for i in range(2, 21):
        if n%i != 0:
            found = True
            break
    if not found:
        break
    n += 20*19*17*13
print(n)
