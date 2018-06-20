# module for predicting scores based on previous games

import numpy as np
from scipy.optimize import minimize
import matplotlib.pyplot as plt
import pickle

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
    # add penalty to normalize average def rating
    drating_sum = 0
    nteams = len(x)/2
    for i in range(nteams):
        drating_sum += x[i*2 + 1]
    davg = drating_sum/nteams
    sum += 100000*((1-davg)**2)
    #print (sum, len(games))
    #exit
    return sum

# gradient of score error function
#
def score_error_gradient(x):
    global games
    nteams = len(x)/2
    gradient = np.array([0]*len(x))
    for g in games:
        if week>0 and g[4] > week:
            continue;
        t1 = g[0]
        t2 = g[1]
        o1_ind = t1*2
        d1_ind = o1_ind+1
        o2_ind = t2*2
        d2_ind = o2_ind+1
        o1 = x[o1_ind]
        d1 = x[d1_ind]
        o2 = x[o2_ind]
        d2 = x[d2_ind]
        p1 = o1*d2
        p2 = o2*d1
        e1 = p1 - g[2]
        e2 = p2 - g[3]
        gradient[o1_ind] += 2*e1*d2
        gradient[o2_ind] += 2*e2*d1
        gradient[d1_ind] += 2*e2*o2
        gradient[d2_ind] += 2*e1*o1
        
    # add component for penalty that normalizes average defensive rating
    sum=0
    for i in range(nteams):
        d_ind = i*2+1
        sum += x[d_ind]
    diff = sum/nteams - 1
    y = 200000*diff/nteams
    for i in range(nteams):
        d_ind = i*2+1
        gradient[d_ind] += y
        
    return gradient/1000.
            
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
    #print(score_error(ratings));
    #print(score_error(ratings - .0001*score_error_gradient(ratings)))
    #return
    #res = minimize(score_error, x0, method='Nelder-Mead', options={'xtol': 1e-2, 'maxfev':1000, 'maxiter': 100000, 'disp': True})

    res = minimize(score_error,x0, jac=score_error_gradient, tol=1e-7, options={'maxiter': 1e8, 'disp': True})
    #res = minimize(score_error,x0,  tol=1e-4, options={'maxiter': 1e8, 'disp': True})
    return res.x


       

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

def prob(t1, t2, r):
    count1 = 0
    count2 = 0
    s1, s2, = predict_score(t1, t2, r)
    for g in games:
        p1, p2 = predict_score(g[0], g[1], r)
        pred1 = s1 + (p1-g[2])
        pred2 = s2 + (p2-g[3])
        if pred1>pred2:
            count1 += 1
        else:
            count2 += 1
    return float(count1)/(float(count1) + float(count2))
def plot_ratings(r):
    offr = []
    defr = []
    n= len(teams)
    for i in range(n):
        offr.append(r[i*2])
        defr.append(r[i*2+1])
    plt.scatter(offr, defr)
    for i, name in enumerate(teams):
        plt.annotate(name, [offr[i], defr[i]])
    plt.ylabel('some numbers')
    plt.show()
def create_info_files(first, last, name):
    for i in range(first, last+1):
        ratings = compute_ratings(i)
        f = open('ratings_'+name+'%d.pickle'%i, 'wb')
        pickle.dump(ratings, f)
        f.close()
        print('finished week %d'%i)
#test()
def create_info_file(name):
        ratings = compute_ratings(0)
        f = open('ratings_'+name+'.pickle', 'wb')
        pickle.dump(ratings, f)
        f.close()
        print('finished week ')
def read_ratings_file(name):
    f = open('ratings_'+name+'.pickle', 'rb')
    x = pickle.load(f)
    f.close()
    return x
