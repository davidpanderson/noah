def e(num):
    x = 1.
    p = 1 + 1./num
    for i in range(num):
        x *= p
    return x
