def pi(n):
    i = 1.
    u = 0
    while i < n:
        m =  1./i
        if ((i - 1) % 4) == 2:
            m = - m
        u = u + m
        i = i + 2
    return 4*u
               
