# compute error
# x: vector of player ratings (off0, def0, off1, def1, ...)
# global: segments
# returns error
#
def nba_error(x):
    global segments
    sum = 0
    for s in segments:
        off0 = 0
        def0 = 0
        off1 = 0
        def1 = 0
        for i in range(5):
            p0 = s['players'][0][i]
            p1 = s['players'][1][i]
            off0 += x[2*p0]
            def0 += x[2*p0+1]
            off1 += x[2*p1]
            def1 += x[2*p1+1]
        pred0 = off0*def1/25
        pred1 = off1*def0/25
        pts0 = s['score'][1][0] - s['score'][0][0]
        pts1 = s['score'][1][1] - s['score'][0][1]
        sum += (pred0-pts0)**2
        sum += (pred1-pts1)**2
    y = 0
    for i in range(nplayers):
        y += x[i*2+1]
    y /= nplayers
    sum += def_weight * (y-1)**2
    return sum
