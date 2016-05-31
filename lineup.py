import random
import itertools
panik = {'name':'panik', 'ab':739, 'hits': 226, 'double':41, 'triple':7, 'hr':12, 'walks': 63}
pagan = {'name':'pagan', 'ab':3673, 'hits': 1033, 'double':201, 'triple':51, 'hr':54, 'walks': 284}
crawford = {'name':'crawford', 'ab':2203, 'hits': 542, 'double':113, 'triple':22, 'hr':49, 'walks': 208}
belt = {'name':'belt', 'ab':1892, 'hits': 516, 'double':118, 'triple':17, 'hr':66, 'walks': 215}
posey = {'name':'posey', 'ab':2813, 'hits': 870, 'double':159, 'triple':6, 'hr':105, 'walks': 287}
duffy = {'name':'duffy', 'ab':724, 'hits': 209, 'double':34, 'triple':7, 'hr':14, 'walks': 36}
pence = {'name':'pence', 'ab':5045, 'hits': 1430, 'double':263, 'triple':47, 'hr':198, 'walks': 412}
span = {'name':'span', 'ab':3906, 'hits': 1119, 'double':192, 'triple':56, 'hr':38, 'walks': 394}
bumgarner = {'name':'bumgarner', 'ab':378, 'hits': 69, 'double':10, 'triple':0, 'hr':12, 'walks': 19}
lineup = [pagan, span, panik, posey, pence, belt, crawford, duffy, bumgarner]

def make_probs(player):
    pa = player['ab'] + player['walks']
    singles = player['hits'] - (player['double'] + player['triple'] + player['hr'])
    single_prob = singles / pa
    double_prob = player['double'] / pa
    triple_prob = player['triple'] / pa
    hr_prob = player['hr'] / pa
    walk_prob = player['walks'] / pa
    player['ps'] = single_prob
    player['psd'] = single_prob + double_prob
    player['psdt'] = single_prob + double_prob + triple_prob
    player['psdth'] = single_prob+ double_prob + triple_prob + hr_prob
    player['psdthw'] = single_prob  + double_prob + triple_prob + hr_prob + walk_prob
    if player['name'] == 'panik':
        print(pa, singles, single_prob, double_prob, triple_prob, hr_prob, walk_prob)
        print(player)

for p in lineup:
    make_probs(p)
    
def at_bat(player):
    n = random.uniform(0, 1)
    x = 0
    if n < player['ps']:
        x = 1
    elif n < player['psd']:
        x = 2
    elif n < player['psdt']:
        x = 3
    elif n < player['psdth']:
        x = 4
    elif n < player['psdthw']:
        x = 5
    #print(n, x)
    return x

def game(lineup, b):
    outs = 0
    inning = 1
    runs = 0
    first = False
    second = False
    third = False
    if b:
        print('inning 1')
    while True:
        for batter in lineup:
            r = at_bat(batter)
            if r == 0:
                outs += 1
                if b:
                    print ('out', batter['name'])
            if r == 1:
                if b:
                    print('single', batter['name'])
                if third != False:
                    if b:
                        print('run scores!', third['name'])
                    runs += 1
                    third = False
                if second != False:
                    if b:
                        print('run scores!', second['name'])
                    runs += 1
                    second = False
                if first != False:
                    second = first
                    first = False
                first = batter
            if r == 2:
                if b:
                    print('double', batter['name'])
                if third != False:
                    if b:
                        print('run scores!', third['name'])
                    runs += 1
                    third = False
                if second != False:
                    if b:
                        print('run scores!', second['name'])
                    runs += 1
                    second = False
                if first != False:
                    if b:
                        print('run scores!', first['name'])
                    runs += 1
                    first = False
                second = batter
            if r == 3:
                if b:
                    print (batter['name'], 'hits a triple')
                if third != False:
                    if b:
                        print('run scores!', third['name'])
                    runs += 1
                    third = False
                if second != False:
                    if b:
                        print('run scores!', second['name'])
                    runs += 1
                    second = False
                if first != False:
                    if b:
                        print('run scores!', first['name'])
                    runs += 1
                    first = False
                third = batter
            if r == 4:
                if b:
                    print( 'home run!', batter['name'])
                if third != False:
                    if b:
                        print('run scored!', third['name'])
                    runs += 1
                if second != False:
                    if b:
                        print('run scored!', second['name'])
                    runs += 1
                if first != False:
                    if b:
                        print('run scored!', first['name'])
                    runs += 1
                    if b:
                        print('run scored!', batter['name'])
                    runs += 1
                    first = False
                    second = False
                    third = False
            if r == 5:
                if b:
                    print('walk', batter['name'])
                if third != False and second != False and first != False:
                    runs += 1
                    if b:
                        print('run scores', third['name'])

                    third = second
                    second = first
                    first = batter
                else:
                    if second != False and first != False:
                        third = second
                        second = first
                        first = batter
                    else:
                        if first != False:
                            second == first
                            first = batter
                        else:
                            first = batter

            if outs == 3:
                first = False
                second = False
                third = False
                inning += 1
                outs = 0
                if inning == 10:
                    return runs
                if b:
                    print('inning', inning)


def test(player):
    total = [0, 0, 0, 0, 0]
    for i in range(734):
        total[at_bat(player)] += 1
    print(total)

def game_test(lineup, n):
    total = 0
    for i in range(n):
        r = game(lineup, True)
        total += r
        print(total/n)
        
def test_lineup(lineup, p):
    total = 0
    for i in range(1, p):
        total += game(lineup, False)
    return total/p

#test(panik)

def print_lineup(lineup):
    for player in lineup:
        print (player['name'])

def find_best_lineup(players):
    lins = 0
    best_lineup = []
    best_score = 0
    for lineup in itertools.permutations(players):
        score = test_lineup(lineup, 500);
        if score > best_score:
            best_lineup = lineup
            print('new best score: ',score, lineup)
            print_lineup(lineup);
            best_score = score
        lins += 1
        if lins % 3628 == 0:
            print (lins/362880., 'percent done')
    return best_lineup

def slg(player):
    b = player['double']*2 + player['triple']*3 + player['hr']*4
    singles = player['hits'] - player['double'] - player['triple'] - player['hr']
    b += singles
    print( b/player['ab'])
#for player in lineup:
    #psc.append([player['name'], test_lineup([player], 10000)])

def test1():
    counter = 0
    ngames = 5
    for i in range(ngames):
        #n = game([panik], False)
        n = game([span, panik, duffy, posey, pence, belt, crawford, bumgarner, pagan], True)
        #print(n, ' runs')
        counter += n
    re = counter/ngames
    print(re)
    
#print (game([panik], True))

#test1()

find_best_lineup(lineup)
