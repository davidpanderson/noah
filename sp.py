# interface to score prediction.

import ncaa_football as ncaa
import nfl as nfl
import score_predict as sp
import pickle
ratings = []
sport = ''
year = ''
def rating_filename(s, y):
    return 'ratings_'+sport+'_'+year
def sp_use(s, y):
    global sport, year, ratings
    sport = s
    year = y
    year = str(year)
    if sport == 'ncaaf':
        ncaa.read_scores(year)
    elif sport == 'nfl':
        nfl.get_games(year)
    else:
        print("no such sport: ", sport)
    try:
        filename = rating_filename(sport, year)
        f = open(filename, 'rb')
        ratings = pickle.load(f)
        f.close()
    except:
        print('run sp_calc')
        

def sp_calc():
    global ratings, sport, year
    ratings = sp.compute_ratings(0)
    filename = rating_filename(sport, year)
    f = open(filename, 'wb')
    pickle.dump(ratings, f)
    f.close()

def sp_teams():
    for t in sp.teams:
        print(sp.teams.index(t), t)

def sp_predict(t1, t2):
    p = sp.predict_score(t1, t2, ratings)
    print(sp.teams[t1], ': ', p[0], sp.teams[t2], ': ', p[1])

def sp_plot():
    sp.plot_ratings(ratings)

def sp_top(which):
    totals = []
    for t in sp.teams:
        i = sp.teams.index(t)
        if which == 'off':
            r = ratings[i*2]
        elif which == 'def':
            r = 1./ratings[i*2+1]
        elif which == 'all':
            r = ratings[i*2]/ratings[i*2+1]
        else:
            print('bad which')
            return
        totals.append([t, r])
    totals.sort(key = lambda x: x[1])
    for t in totals:
        print(t[0], ': ', t[1])
