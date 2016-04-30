import pickle
import football2 as fb
import numpy as np
from scipy.optimize import minimize

def int_check(x):
    try:
        int(x)
        return True
    except:
        return False
    
teams = ['Bears',
    'Bengals',
    'Bills',
    'Broncos',
    'Browns',
    'Buccaneers',
    'Cardinals',
    'Chargers',
    'Chiefs',
    'Colts',
    'Cowboys',
    'Dolphins',
    'Eagles',
    'Falcons',
    'Giants',
    'Jaguars',
    'Jets',
    'Lions',
    'Packers',
    'Panthers',
    'Patriots',
    'Raiders',
    'Rams',
    'Ravens',
    'Redskins',
    'Saints',
    'Seahawks',
    'Steelers',
    'Texans',
    'Titans',
    'Vikings',
    '49ers']

week = 0
def get_games():
    global week, teams
    games = []
    t1 = ''
    s1 = ''
    t2 = ''
    s2 = ''
    print (teams)
    f = open('nfl_scores.txt', 'r')
    for line in f:
        line = line.strip()
        if line == '':
            continue
        #print('%s: t1 %s t2 %s s1 %s s2 %s' %(line, t1,t2,s1,s2))
        if line in teams:
            if t1 == '':
                t1 = line
                continue
            if t2 == '':
                t2 = line
                continue
        elif int_check(line):
            if s1 == '':
                s1 = line
            elif s2 == '':
                s2 = line
                s1 = int(s1)
                s2 = int(s2)
                game = [
                    teams.index(t1), teams.index(t2),
                    s1, s2,
                    week
                    ]
                games.append(game)
                t2 = ''
                s1 = ''
                s2 = ''
                t1 = ''
        else:
            if line.startswith('Thursday'):
                week += 1
    return games

iter = 1

def score_error(x):
    global games
    global iter
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
    iter += 1
    if iter % 1000 == 0:
        print (iter, sum, len(games))
    return sum

def compute_ratings(wk):
    global teams, games, week
    ratings = []
    for t in teams:
        ratings.append(20)
        ratings.append(1)
    x0 = np.array(ratings)
    week = wk
    print('calling min')
    res = minimize(score_error, x0, method='Nelder-Mead', options={'ftol': 1e-1, 'xtol': 1e-4, 'maxfev':1000000, 'maxiter': 1000000000, 'disp': True})
    return res.x

def create_info_files():
    x = get_games()
    x = [teams, x]
    f = open('data.pickle', 'wb')
    pickle.dump(x, f)
    f.close()
#    for i in range(1,14):
    for i in range(1,2):
        ratings = compute_ratings(i)
        f = open('nfl_ratings_2%d.pickle'%i, 'wb')
        pickle.dump(ratings, f)
        f.close()
        print('finished week %d'%i)
        
def read_ratings_file(week):
    f = open('nfl_ratings_%d.pickle'%week, 'rb')
    return f
    x = pickle.load(f)
    f.close()
    return x

def rankings(week):
    count = 0
    ratings = compute_ratings(week)
    print(ratings)
    pairs = {}
    totals = []
    for team in teams:
        print(team)
        r = ratings[count * 2] / ratings[count*2+1]
        print('yes')
        pairs[r] = team
        print('yes')
        print(r)
        totals.append(r)
        count += 1
    totals.sort()
    print(totals)
    count = 0
    for t in totals:
        print(32-count, t, pairs[t])
        count += 1



games = get_games()
#print(week)
#print(games)
#print(len(games))
ratings = compute_ratings(week)
#print(fb.predict_score(teams.index('Panthers'), teams.index('Broncos'), ratings))
print(rankings(6))
#print(read_ratings_file(21))
                
            
