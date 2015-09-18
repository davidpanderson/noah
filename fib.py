def fib(n):
    f = [0, 1]
    for i in range(2, n):
        f.append(f[i-1] + f[i-2])
    return f

def ben():
    d = 0
    f = fib(50)
    for i in range(50):
        print f[i]
        s = str(f[i])
        if s[0] == '1':
            d += 1
    return float(d)/50.

print ben()
