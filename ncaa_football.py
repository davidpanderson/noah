import score_predict as fb
import pickle
import math
#import spread_predict as sp

ratings = []

# return whether a line starts with an integer character
def int_check(c):
    if c == '':
        return False
    d = c[0]
    return d.isdigit()

# returns list of lines in score file
# current score file is from http://www.jhowell.net/cf/scores/Sked2017.htm
def read_scores(year):
    w = []
    f = open('college_football_'+year+'.txt', 'r')
    print (f)
    for line in f:
        line = line.strip()
        if line != '':
            w.append(line)
    f.close()
    return w

# given a line of the form "teamname (conf)", return teamname
# teamname may contain (, e.g. Miami (Florida) (ACC)
#
def team_name(line):
    n = line.rfind('(')
    return line[:n-1]
                    
# read score file, put list of teams in fb.teams
#
def get_teams(year):
    pcount = 0
    fb.teams = []
    f = read_scores(year)      
    for l in f:
        if int_check(l):
            continue
        fb.teams.append(team_name(l))

# parse the score file, create fb.teams and fb.games global variables
#
def get_games(year):
    fb.games = []
    get_teams()
    f = read_scores(year)
    week = 0
    for line in f:
        words = line.split('\t')
        if len(words) >= 7:
            if not int_check(words[5]):
                continue
            if not int_check(words[6]):
                continue
            week += 1
            #print(line)
            t2 = words[3].replace('*', '')
            if t1 > t2:
                continue
            if t2 not in fb.teams:
                #print(t2, ' not found; skipping ', line)
                continue
            game = [
                fb.teams.index(t1), fb.teams.index(t2),
                int(words[5]), int(words[6]),
                week
                ]
            fb.games.append(game)
        else:
             t1 = team_name(line)
             week = 0

def get_games_new():
    x = ['vs.', '@']
    nuetral = False
    fb.games = []
    get_teams()
    f = read_scores()
    for line in f:
        words = line.split('\t')
        if len(words) >= 7:
            if not int_check(words[5]):
                continue
            if not int_check(words[6]):
                continue
            try:
                v = words[8]
                nuetral = True
            except:
                nuetral = False
                week += 1
           #print(line)
            t2 = words[3].replace('*', '')
            if t1 > t2:
                continue
            if  t2 not in fb.teams:
                #print(t2, ' not found; skipping ', line)
                continue
            if nuetral == False:
                game = [
                    fb.teams.index(t1), fb.teams.index(t2),
                    int(words[5]), int(words[6]),
                    week, x.index(words[2])
                    ]
                #print(game)
                fb.games.append(game)
            else:
                game = [
                    fb.teams.index(t1), fb.teams.index(t2),
                    int(words[5]), int(words[6]),
                    week, 2]
                #print(game)
            
                fb.games.append(game)
        else:
             words = line.split(' (')
             t1 = words[0]
             week = 0
             
# creates files with the ratings for each team for each week


# adds all the names of the teams to fb.teams
def read_info_file():
    global teams, games
    f = open('data.pickle', 'rb')
    x = pickle.load(f)
    f.close()
    fb.teams = x[0]
    fb.games = x[1]
    
# reads the ratings files for a particular week
def read_ratings_file(week):
    f = open('ratings_17_2%d.pickle'%week, 'rb')
    x = pickle.load(f)
    f.close()
    return x

# prints rankings
def rankings():
    count = 0
  #  ratings = read_ratings_file(week)
  #  read_info_file()
    ratings = fb.compute_ratings(0)
    pairs = {}
    totals = []
    for team in fb.teams:
        r = ratings[count * 2] / ratings[count*2+1]
        pairs[r] = team
        totals.append(r)
        count += 1
    totals.sort()
    count = 0
    for t in totals:
        print(128-count+2  ,t, pairs[t])
        count += 1

# check whether any teams have no games through given week
#
def check_teams_have_games(week):
    nteams = len(fb.teams)
    ngames = [0]*nteams
    for game in fb.games:
        if game[4] > week:
            continue;
        ngames[game[0]] += 1
        ngames[game[1]] += 1
    for i in range(nteams):
        print("team %s has played %d games" %(fb.teams[i], ngames[i]))
        
def test():
    get_games()
    print(games)
    print(len(games))
    
# prints the scores for a game
def test_predict():
   # read_info_file()
    #ratings = read_ratings_file(13)
    #print(fb.teams)
    ratings = fb.compute_ratings(0)
    input1 = 'Wisconsin'
    input2 = 'Miami (Florida)'
    t1 = fb.teams.index(input1)
    t2 = fb.teams.index(input2)

    p = fb.predict_score(t1, t2, ratings)
    print(input1, p[0], input2, p[1])
    
def wk_error(wk):
    sum = 0
    get_games()
    ratings = read_ratings_file(wk)
    wk_games = []
    print('week ', wk)
    print(len(fb.games), ' total games')
    for game in fb.games:
        if game[4] == wk + 1:
            wk_games.append(game)
    print(len(wk_games), ' games')
    nwin = 0
    for game in wk_games:
        p_score = fb.predict_score(game[0], game[1], ratings)
        p_spread = p_score[0] - p_score[1]
        r_spread = game[2] - game[3]
        if p_spread < 0 and r_spread < 0:
            nwin += 1
        if p_spread > 0 and r_spread > 0:
            nwin += 1
        diff = (p_spread - r_spread)
        #print(p_spread, r_spread, diff)
        sum += diff*diff 
    #print(sum, len(wk_games))
    ave = sum/len(wk_games)
    ave = math.sqrt(ave)
    print('points off per game:', ave)
    per = 100 * nwin/len(wk_games)
    print("predict right winner ", nwin, " out of ", len(wk_games), per)

#takes a method and method files and sees how good the method is
def Method_test(method):
    pass

    #return ave
    

    #wk_error(i)
#create_info_files()

#wk_error(1)
#print(test_predict())
#while True:
  #  i = input()
def view_games(wk):
    global games, teams
    for g in fb.games:
        if g[4] <= wk:
            print('team %s %s, team %s %s, week %s' %(fb.teams[g[0]], g[2], fb.teams[g[1]], g[3], g[4]))

def score_error_true_1(x, ho):
    global games
    sum = 0
    for g in fb.games:
        o1 = x[g[0]*2]
        d1 = x[g[0]*2+1]
        o2 = x[g[1]*2]
        d2 = x[g[1]*2+1]
        if x[2] == 0:
            p1 = o1*d2*xho
            p2 = o2*d1/ho
        elif x[2] == 1:
            p2 = o2*d1*ho
            p1 = o1*d2/ho
        elif x[2] == 2:
            p2 = o2*d1
            p1 = o1*d2
        e1 = p1 - g[2]
        e2 = p2 - g[3]
        sum += e1**2
        sum += e2**2
        sum += (d1-1)**2
        sum += (d2-1)**2
    return sum

def avg_def_rating(r):
    sum = 0
    nteams = len(fb.teams)
    for i in range(nteams):
        sum += r[i*2+1];
    print("avg def rating: ", sum/nteams)

def read_spread_file():
    f = open('spreads16-17.txt', 'r')
    f = list(f)
    games = []
    g = []
    counter = 0
    for e in f:
        e = e.split(',')
        counter +=1
        if counter == 3:
            counter = 1
            g = []
            games.append(g)
        for x in e:
            g.append(x)
        print (games)
    
     # add penalty to normalize average def rating
    rating_sum = 0
    nteams = len(x)
    
def spread_score(wk):
    global teams, games 
    print (fb.teams)
    sp.teams = fb.teams
    sp.games = fb.games
    test = []
    for g in fb.games:
        if g[4] > wk:
            test.append(g)  
    score_ratings = fb.compute_ratings(wk-1)
    diff_ratings = sp.compute_ratings(wk-1)
    spread_error = 0
    score_error = 0
    for g in test:
        score1 = score_ratings[g[0]*2]*score_ratings[g[0]*2+1]
        score2 = score_ratings[g[1]*2]*score_ratings[g[1]*2+1]
        score_error += (score1-score2-g[2]+g[3])**2
        score1 = diff_ratings[g[0]*2]*diff_ratings[g[0]*2+1]
        score2 = diff_ratings[g[1]*2]*diff_ratings[g[1]*2+1]
        spread_error += (score1-score2-g[2]+g[3])**2
    print (spread_error, score_error, len(test))

#get_teams()
#get_games()
#rankings()
#r = fb.read_ratings_file('ncaa_football18')
#fb.plot_ratings(r)

