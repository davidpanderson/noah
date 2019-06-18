# error function and gradient for NBA player analysis

import numpy as np

# in the error function we add an error term to make the
# defensive weights average to 1.
# This is the coefficient of the error term
#
def_weight = 1.e6

# compute average off/def ratings of 5 players
# x: vector of player ratings (off0, def0, off1, def1, ...)
#
def rating_avgs(players, x):
    osum = 0
    dsum = 0
    for pid in players:
        pseq = nba.player_seqno[pid]
        osum += x[2*pseq]
        dsum += x[2*pseq+1]
    return [osum/5, dsum/5]

# compute error
# x: vector of player ratings (off0, def0, off1, def1, ...)
# global: segments
# returns error
#
def nba_error(x):
    global nba
    sum = 0
    for s in nba.trimmed_segs:
        r = []
        for t in range(2):
            r.append(rating_avgs(s['players'][t], x))
        for ta in range(2):
            tb = 1 - ta
            predicted = r[ta][0]*r[tb][1]*s['duration']
            actual = s['points_scored'][ta]
            sum += (predicted - actual)**2
    dsum = 0
    nplayers = int(len(x)/2)
    for i in range(nplayers):
        dsum += x[i*2+1]
    davg = dsum/nplayers
    sum += def_weight * (davg-1)**2
    print(sum)
    return sum

def nba_error_gradient(x):
    gradient = np.array([0.0]*len(x))
    for s in nba.trimmed_segs:
        r = []
        for t in range(2):
            r.append(rating_avgs(s['players'][t], x))
        pred = []
        ps = []
        for ta in range(2):
            tb = 1 - ta
            pred.append(r[ta][0]*r[tb][1]*s['duration'])
            ps.append(s['points_scored'][ta])
        for ta in range(2):
            tb = 1 - ta
            for pid in s['players'][ta]:
                pseq = nba.player_seqno[pid]
                #if ps[0] > 1000 or ps[0] < 0:
                #print(pred, ps, r)
                gradient[pseq*2] += 2.*(pred[ta] - ps[ta])*r[tb][1]
                gradient[pseq*2+1] += 2.*(pred[tb] - ps[tb])*r[tb][0]

    dsum = 0
    nplayers = int(len(x)/2)
    for i in range(nplayers):
        dsum += x[2*i+1]
    davg = dsum/nplayers
    for i in range(nplayers):
        gradient[2*i+1] += 2.*def_weight*(davg-1)/nplayers
        
    return gradient
