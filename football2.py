import numpy as np
from scipy.optimize import minimize

teams = []
games = []
week = 13

# a game is described by a list
# team1 (int), team2 (int), score1, score2, week

# x is list of team offense/defense estimates
# x[0]/x[1]: off/def for team 0
# x[2]/x[3]: off/def for team 1
# ...
def score_error(x):
    global games
    we = 1
    c_week = 1
    sum = 0
    for g in games:
        if g[4] > week:
            continue
        if g[4] > c_week:
            we *= 1.2
        o1 = x[g[0]*2]
        d1 = x[g[0]*2+1]
        o2 = x[g[1]*2]
        d2 = x[g[1]*2+1]
        p1 = o1*d2
        p2 = o2*d1
        e1 = p1 - g[2]
        e1 *= we
        e2 = p2 - g[3]
        e2 *= we
        sum += e1**2
        sum += e2**2
        sum += (d1-1)**2
        sum += (d2-1)**2
    return sum

def predict_score(i, j, x):
    o1 = x[i*2]
    d1 = x[i*2+1]
    o2 = x[j*2]
    d2 = x[j*2+1]
    p1 = o1*d2
    p2 = o2*d1
    #print(teams[i], o1, d1, teams[j], o2, d2, p1, p2)
    return [p1, p2]

def compute_ratings(wk):
    global teams, games, week
    ratings = []
    for t in teams:
        ratings.append(20)
        ratings.append(1)
    x0 = np.array(ratings)
    week = wk
    res = minimize(score_error, x0, method='Nelder-Mead', options={'xtol': 1e-8, 'maxfev':1000000, 'maxiter': 1000000, 'disp': True})
    return res.x

def test():
    global teams, games
    teams = ['Berkeley Bumblebees', 'Albany Anteaters', 'Emeryville Escargot']

    g1 = Game(0, 1, 21, 14)
    g2 = Game(1, 2, 28, 7)
    games = [g1, g2]

    x = compute_ratings()
    print(teams)
    print(x)
    for i in range(3):
        for j in range(i+1, 3):
            predict_score(i, j, x)


        

        

    
    

