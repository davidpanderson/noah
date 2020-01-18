import score_predict as sp

sp.teams = []
sp.games = []

#read scores from file
#https://www.scoreboard.com/nfl/results/
def read_scores(year):
    w = []
    f = open('nfl_scores'+year+'.txt', 'r')
   # f = open('ncaa_basketball2019.txt', 'r')
    print (f)
    for line in f:
        line = line.strip()
        if line != '':
            w.append(line)
    f.close()
    return w

#divide the lines into a list of games
#each game is the date, the first team, @ the home team, and the score.
# if the game goes into OT, there will also be the score before OT
def read_games(year):
    lines = read_scores(year)
    games = []
    g = []
    for line in lines:
        if len(g) <4:
            g.append(line)
            continue
        if line[0] == '(':
            g.append(line)
            games.append(g)
            g = []
            continue
        games.append(g)
        g = [line]
    if len(g) > 0:
        games.append(g)
    return games

#puts list of teams in sp.teams
def get_teams(games):
    for g in games:
        if g[1] not in sp.teams:
            sp.teams.append(g[1])
        t2 = g[2]
        t2 = t2[2:]
        if t2 not in sp.teams:
            sp.teams.append(t2)

def get_games(year):
    games = read_games(year)
    get_teams(games)
    for g in games:
        x = g[3].split(' : ')
        y = [
            sp.teams.index(g[1]),
            sp.teams.index(g[2][2:]),
            int(x[0]),
            int(x[1]),
            0
        ]
        sp.games.append(y)
   
#get_games(2019)
#r = sp.compute_ratings(0)
#sp.plot_ratings(r)
