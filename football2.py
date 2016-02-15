import numpy as np
from scipy.optimize import minimize

# global variables
teams = []
games = []
week = 13

# a game is described by a list
# team1 (int), team2 (int), score1, score2, week

# base model: each team has off/def ratings
# model options:
#   - aging: games are weighted by age_param^week
#   - home field advantage:
#   - over_under: it true, optimize point total
#      otherwise optimize individual scores

# compute model error
# this is called by the optimize function
# x is list of team ratings
# x[0]/x[1]: off/def for team 0
# x[2]/x[3]: off/def for team 1
# ...
def score_error(x):
    global games
    sum = 0
    for g in games:
        o1 = x[g[0]*2]
        d1 = x[g[0]*2+1]
        o2 = x[g[1]*2]
        d2 = x[g[1]*2+1]
        p1 = o1*d2
        p2 = o2*d1
        e1 = p1 - g[2]
        e2 = p2 - g[3]
        sum += e1**2
        sum += e2**2
        sum += (d1-1)**2
        sum += (d2-1)**2
    #print (sum, len(games))
    exit
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
    res = minimize(score_error, x0, method='Nelder-Mead', options={'xtol': 1e-8, 'maxfev':1000000, 'maxiter': 1000000000, 'disp': True})
    return res

def test():
    global teams, games
    teams = ['Berkeley Bumblebees', 'Albany Anteaters', 'Emeryville Escargot']
    g1 = [0, 1, 21, 14]
    g2 = [1, 2, 28, 7]
    games = [g1, g2]

    x = compute_ratings(1)
    print(x)
    print(predict_score(0, 1, x))
    #print(teams)
    #print(x)
    #for i in range(3):
     #   for j in range(i+1, 3):
      #      return predict_score(teams[0], teams[1], x)
