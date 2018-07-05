# compute error
# x: vector of player ratings (off0, def0, off1, def1, ...)
# global: segments
# returns error
#
import numpy as np
def_weight = 1000000.

def rating_sums(players, x):
    osum = 0
    dsum = 0
    for pid in players:
        pseq = nba.id_to_seq(pid)
        osum += x[2*pseq]
        dsum += x[2*pseq+1]
    return [osum, dsum]

def nba_error(x):
    global nba
    sum = 0
    for s in nba.segs:
        for t in range(2):
            r[t] = rating_sums(s['players'][t], x)
        for ta in range(2):
            tb = 1 - ta
            pred = r[ta][0]*r[tb][1]*s['duration']
            ps = s['points_scored'][ta]
            sum += (pred - ps)**2
    y = 0
    for i in range(nplayers):
        y += x[i*2+1]
    y /= nplayers
    sum += def_weight * (y-1)**2
    return sum

def nba_error_gradient(x):
    gradient = np.array([0]*len(x))
    for s in nba.segs:
        for t in range(2):
            r[t] = rating_sums(s['players'][t], x)
        for t in range(2):
            pred[t] = r[t][0]*r[1-t][1]*s['duration']
            ps[t] = s['points_scored'][t]
        for ta in range(2):
            tb = 1 - ta
            for pid in s['players'][ta]:
                pseq = nba.id_to_seq(pid)
                gradient[pseq*2] += 2*(pred[ta] - ps[ta])*r[tb][1]
                gradient[pseq*2+1] += 2*(pred[tb] - ps[tb])*r[tb][0]

    dsum = 0
    for i in range(len(x)/2):
        dsum += x[2*i+1]
    davg = dsum/len(x)/2
    for i in range(len(x)/2):
        gradient[2*i+1] += 2*def_weight*(davg-1)
        
    return gradient
