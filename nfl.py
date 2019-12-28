import score_predict as sp

sp.teams = []
sp.games = []

#read scores from file
#https://www.scoreboard.com/nfl/results/
def read_scores():
    w = []
    f = open('nfl_scores2019.txt', 'r')
    print (f)
    for line in f:
        line = line.strip()
        if line != '':
            w.append(line)
    f.close()
    return w

#
def get_games():
    lines = read_scores()
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

def get
