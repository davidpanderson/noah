import numpy as np
from scipy.optimize import minimize

class Team:
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return 'name: %s' % (self.name)

class Game:
    def __init__(self, team1, team2, score1, score2):
        self.team1 = team1  # index of team in teams list
        self.team2 = team2
        self.score1 = score1
        self.score2 = score2

t1 = Team('Berkeley Bumblebees')
t2 = Team('Albany Anteaters')
t3 = Team('Emeryville Escargot')
teams = [t1, t2, t3]

g1 = Game(0, 1, 21, 14)
g2 = Game(1, 2, 28, 7)
games = [g1, g2]

print(teams)

# x is list of team offense/defense estimates
# x[0]/x[1]: off/def for team 0
# x[2]/x[3]: off/def for team 1
# ...
def score_error(x):
    sum = 0
    for g in games:
        o1 = x[g.team1*2]
        d1 = x[g.team1*2+1]
        o2 = x[g.team2*2]
        d2 = x[g.team2*2+1]
        p1 = o1*d2
        p2 = o2*d1
        e1 = p1 - g.score1
        e2 = p2 - g.score2
        sum += e1**2
        sum += e2**2
        sum += (d1-1)**2
        sum += (d2-1)**2
    return sum

def predict_score(i, j, x):
    o1 = x[i*2]
    d1 = x[i*2+1]
    o2 = x[j*2]
    d2 = x[j*2+1]
    p1 = o1*d2
    p2 = o2*d1
    team1 = teams[i]
    team2 = teams[j]
    print(team1.name, p1, team2.name, p2)

def foo2():
    x0 = np.array([10, 1, 10, 1, 10, 1])
    res = minimize(score_error, x0, method='powell', options={'xtol': 1e-8, 'disp': True})
    print(res.x)
    for i in range(3):
        for j in range(i+1, 3):
            predict_score(i, j, res.x)

foo2()
