from football2 import *
import pickle

def r():
    w = []
    f = open('ncaa_football.txt', 'r')
    for line in f:
        line = line.strip()
        if line != '':
            w.append(line)
    return w

def get_teams():
    f = r()
    for l in f:
        x = True
        try:
            int(l[0])
        except:
            x = False
            
        if x == False:
            l = l.split(' (')
            teams.append(l[0])

#ts = teams()            
#for t in ts:
#    print(t)
   
def int_check(c):
    try:
        int(c)
    except:
        return False
    return True

# parse the data file, create teams and games global variables
#
def get_games():
    get_teams()
    f = r()
    for line in f:
        words = line.split('\t')
        if len(words) >= 7:
            #print(line)
            t2 = words[3].replace('*', '')
            if t1 > t2:
                continue
            if  t2 not in teams:
                continue
            if not int_check(words[5]):
                continue
            if not int_check(words[6]):
                continue
            d = [
                teams.index(t1), teams.index(t2),
                int(words[5]), int(words[6])
                ]
            games.append(d)
        else:
             words = line.split(' (')
             t1 = words[0]

def create_info_file():
    get_games()
    ratings = predict()
    x = [teams, games, ratings]
    f = open('data.pickle', 'wb')
    pickle.dump(x, f)
    f.close()
    print('done')

def read_info_file():
    global teams, games
    f = open('data.pickle', 'rb')
    x = pickle.load(f);
    f.close();
    teams = x[0]
    games = x[1]
    return x[2]

def rankings():
    count = 0
    ratings = read_info_file()
    pairs = {}
    totals = []
    for team in teams:
        r = ratings[count * 2] / ratings[count*2+1]
        pairs[r] = team
        totals.append(r)
        count += 1
    totals.sort()
    count = 0
    for t in totals:
        print(128-count, t, pairs[t])
        count += 1
        

def test():
    get_games()
    print(games)
    print(len(games))
    ratings = predict()
    predict_score(9, 6, ratings)

rankings()
 
    
