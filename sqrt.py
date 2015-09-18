def sqrt(x):
    if x > 1:
        s = 1
        g = x
    else:
        s = x
        g = 1
    for i in range(20):
        m = float((g + s)/2)
        if m * m > x:
            g = m
        else:
            s = m
        print m


sqrt(.25)
