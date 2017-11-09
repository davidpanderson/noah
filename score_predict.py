# module for predicting scores based on previous games

import numpy as np
from scipy.optimize import minimize
# global variables
teams = []
games = []
week = 0

# a game is described by a list
# team1 (int), team2 (int), score1, score2, week

# base model: each team has off/def ratings
# model options:
#   - aging: games are weighted by age_param^week
#   - home field advantage:
#   - over_under: it true, optimize point total
#      otherwise optimize individual scores

# compute model error based on games in weeks 1..week
# this is called by the optimize function
# x is list of team ratings
# x[0]/x[1]: off/def for team 0
# x[2]/x[3]: off/def for team 1
# ...
def score_error(x):
    global games
    sum = 0
    for g in games:
        if week>0 and g[4] > week:
            continue;
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
    drating_sum = 0
    nteams = len(x)/2
    for i in range(nteams):
        drating_sum += x[i*2 + 1]
    davg = drating_sum/nteams
    sum += (1-davg)**2
    #print (sum, len(games))
    #exit
    return sum

# predict score of game between i and j, given ratings in x
def predict_score(i, j, x):
    o1 = x[i*2]
    d1 = x[i*2+1]
    o2 = x[j*2]
    d2 = x[j*2+1]
    p1 = o1*d2
    p2 = o2*d1
    #print(teams[i], o1, d1, teams[j], o2, d2, p1, p2)
    return [p1, p2]

# compute ratings based on weeks 1..wk
def compute_ratings(wk):
    global teams, games, week
    ratings = []

    # initial values: offense 20, defense 1
    for t in teams:
        ratings.append(20)
        ratings.append(1)
    x0 = np.array(ratings)
    week = wk
    #res = minimize(score_error, x0, method='Nelder-Mead', options={'xtol': 1e-2, 'maxfev':1000, 'maxiter': 100000, 'disp': True})

    res = minimize(score_error, x0,  tol=1e-4, options={'maxiter': 1e8, 'disp': True})
    return res.x

def view_games(wk):
    global games, teams
    for g in games:
        if g[4] <= wk:
            print('team %s %s, team %s %s, week %s' %(teams[g[0]], g[2], teams[g[1]], g[3], g[4]))
       

def test():
    global teams, games
    teams = ['Berkeley Bumblebees', 'Albany Anteaters', 'Emeryville Escargot']
    g1 = [0, 1, 21, 14, 1]
    g2 = [1, 2, 28, 7, 1]
    games = [g1, g2]

    x = compute_ratings(0)
    #print(predict_score(0, 2, x))
    print(teams)
    print(x)
    for i in range(3):
        for j in range(i+1, 3):
            print( predict_score(i,j , x))

# are teams fully connected by games through week N?
#
def fully_connected(week):
    global teams, games
    # list of lowest team # team i is connected to by games
    #
    lowest = list(range(len(teams)))
    while True:
        changed = False
        for game in games:
            if game[4] > week:
                continue
            t0 = game[0]
            t1 = game[1]
            if lowest[t0] < lowest[t1]:
                changed = True
                lowest[t1] = lowest[t0]
            elif lowest[t1] < lowest[t0]:
                changed = True
                lowest[t0] = lowest[t1]
        if not changed:
            break
    return all(v == 0 for v in lowest)

test()
