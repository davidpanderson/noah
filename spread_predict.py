import numpy as np
from scipy.optimize import minimize
import math
penalty_scale = 100000
week = 11
def diff_error_old(x):
    global games, penaly_scale
    sum = 0
    for g in games:
        if week>0 and g[4] > week:
            continue;
        d = g[2] - g[3]
        sum += (x[g[0]] - x[g[1]] - d) ** 2
     # add penalty to normalize average def rating
    rating_sum = 0
    nteams = len(x)
    for i in range(nteams):
        rating_sum += x[i]
    avg = rating_sum/nteams
    sum += penalty_scale*((avg)**2)
    return sum

def diff_error_old_grad(x):
    global games, teams, penalty_scale
    nteams = len(x)
    gradient = np.array([0]*nteams)
    for g in games:
        if week>0 and g[4] > week:
            continue;
        d = g[2] - g[3]
        gradient[g[0]] += 2*(x[g[0]] - x[g[1]] - d)
        gradient[g[1]] -= 2*(x[g[0]] - x[g[1]] - d)
    avg = 0
    for r in x:
        avg += r
    avg /= nteams
    for r in range(nteams):
        gradient[r] += penalty_scale*2*avg/nteams
    return gradient

# compute ratings based on weeks 1..wk
def compute_ratings_old(wk):
    global teams, games, week
    ratings = []

    for t in teams:
        ratings.append(0)
    x0 = np.array(ratings)
    week = wk
    #print(score_error(ratings));
    #print(score_error(ratings - .0001*score_error_gradient(ratings)))
    #return
    #res = minimize(score_error, x0, method='Nelder-Mead', options={'xtol': 1e-2, 'maxfev':1000, 'maxiter': 100000, 'disp': True})
    res = minimize(diff_error,x0, jac=diff_error_grad, tol=1e-7, options={'maxiter': 1e1000, 'disp': True})
    #res = minimize(score_error,x0,  tol=1e-4, options={'maxiter': 1e8, 'disp': True})
    return res.x

def diff_error_test(x):
    global games, penaly_scale
    sum = 0
    for g in games:
        if week>0 and g[4] > week:
            continue;
        d = g[2] - g[3]
        o1 = x[g[0]*2]
        d1 = x[g[0]*2+1]
        o2 = x[g[1]*2]
        d2 = x[g[1]*2+1]
        p1 = o1*d2
        p2 = o2*d1
        d = g[2]-g[3]
        sum += math.sqrt((p1 - p2 - d) ** 2)
    rating_sum = 0
    nteams = len(x)
    ngames = len(games)
    sum /= ngames
#    sum = math.sqrt(sum)
    return sum

def test_team(team):
    x = compute_ratings(0)
    for g in games:
        if g[0] == team or g[1] == team:
            print teams[g[0]]
            print teams[g[1]]
            print 'score ', g[2], g[3]
            print 'predicted differince', x[g[0]] - x[g[1]]
                    


def diff_error(x):
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
        d = g[2]-g[3]
        sum += (p1 - p2 - d) ** 2
    # add penalty to normalize average def rating
    drating_sum = 0
    nteams = len(x)/2
    for i in range(nteams):
        drating_sum += x[i*2 + 1]
    davg = drating_sum/nteams
    sum += penalty_scale*((1-davg)**2)
    #print x[0], sum
    return sum

def diff_error_gradient(x):
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
        e = (p1 - p2 - (g[2] - g[3]))
        gradient[o1_ind] += 2*e*d2
        gradient[o2_ind] -= 2*e*d1
        gradient[d1_ind] -= 2*e*o2
        gradient[d2_ind] += 2*e*o1
     
 # add component for penalty that normalizes average defensive rating
    sum=0
    for i in range(nteams):
        d_ind = i*2+1
        sum += x[d_ind]
    diff = sum/nteams - 1
    y = penalty_scale*diff/nteams
    for i in range(nteams):
        d_ind = i*2+1
        gradient[d_ind] += y
        
    return gradient/10000.
        
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

    res = minimize(diff_error,x0, jac=diff_error_gradient, tol=1e-7, options={'maxiter': 1e8, 'disp': True})
    #res = minimize(score_error,x0,  tol=1e-4, options={'maxiter': 1e8, 'disp': True})
    return res.x

def predict_spread(t1, t2):
    r = compute_ratings(0)
    t1 = teams.index(t1)
    t2 = teams.index(t2)
    score1 = r[t1*2] * r[t2*2 + 1]
    print t1
    print t2
    print score1
    score2 = r[t2*2] * r[t1 * 2 + 1]
    print score2
    print r[t1*2]
    print r[t1*2 + 1]
    print r[t2*2]
    print r[t2*2 + 1]

    print score1 - score2

