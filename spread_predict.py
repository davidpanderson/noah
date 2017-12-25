import numpy as np
from scipy.optimize import minimize
penalty_scale = 100000
def diff_error(x):
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

def diff_error_grad(x):
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
def compute_ratings(wk):
    global teams, games, week
    ratings = []

    # initial values: offense 20, defense 1
    for t in teams:
        ratings.append(0)
    x0 = np.array(ratings)
    week = wk
    #print(score_error(ratings));
    #print(score_error(ratings - .0001*score_error_gradient(ratings)))
    #return
    #res = minimize(score_error, x0, method='Nelder-Mead', options={'xtol': 1e-2, 'maxfev':1000, 'maxiter': 100000, 'disp': True})
    res = minimize(diff_error,x0, jac=diff_error_grad, tol=1e-7, options={'maxiter': 1e8, 'disp': True})
    #res = minimize(score_error,x0,  tol=1e-4, options={'maxiter': 1e8, 'disp': True})
    return res.x

    

        

