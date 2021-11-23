from openpyxl import load_workbook
import score_predict as fb
lines = []
def load_file(filename):
    global lines
    file = load_workbook(filename)
    file = file.active
    lines = list(file.values)
    del lines[0]

#put list of teams in fb.teams
def get_teams():
    for row in lines:
       if row[3] not in fb.teams:
           fb.teams.append(row[3])

#gets list of games in fb.games
def get_games():
    for i in range(int(len(lines)/2)):
        # try except because of nonetype
        try: 
            t1 = int(fb.teams.index(lines[i*2][3]))
            t2 = int(fb.teams.index(lines[i*2+1][3]))
            score1 = int(lines[i*2][8])
            score2 = int(lines[i*2+1][8])
      #      if type(score1) == 'NoneType' or type(score2) == 'NoneType' or type(t1) == 'NoneType' or type{t2 == 'NoneType':
      #          continue
      #      else:
            fb.games.append([t1, t2, score1, score2, 1])
        except:
            continue

#See how often the program gets the vegas line right
# date is the number of the date that seperates the games to use to
# compute ratings. and the ones to test.
def compare_vegas(date):
    vegas_tally = 0
    p_tally = 0
    fb.games = []
    for i in range(int(len(lines)/2)):
        if lines[i*2][0] <= date:
            try: 
                t1 = int(fb.teams.index(lines[i*2][3]))
                t2 = int(fb.teams.index(lines[i*2+1][3]))
                score1 = int(lines[i*2][8])
                score2 = int(lines[i*2+1][8])
          #      if type(score1) == 'NoneType' or type(score2) == 'NoneType' or type(t1) == 'NoneType' or type{t2 == 'NoneType':
          #          continue

          #      else:
                fb.games.append([t1, t2, score1, score2, 1])
            except:
                continue
    r = fb.compute_ratings(0)
  #  print(fb.games)
    for i in range(int(len(lines)/2)):
        try:
            if lines[i*2][0] > date:
                o1 = float(lines[i*2][10])
                o2 = float(lines[i*2+1][10])
                if o1<o2:
                    spread = o1
                else:
                    spread = o2*-1
           #     print(spread)
           #     print('yeet')
                t1 = int(fb.teams.index(lines[i*2][3]))
                t2 = int(fb.teams.index(lines[i*2+1][3]))
             #   print('yeet')
                p = fb.predict_score(t1, t2, r)
               # print(p)
                d = (p[0]-p[1])-spread
              #  print(d)
                margin = int(lines[i*2][8])-int(lines[i*2+1][8])
                print(margin)
                if d>9:
                    if d*(margin-spread) >0:
                        p_tally +=1
                        print('spread', spread, 'prediction:', p, 'won')
                    else:
                        vegas_tally += 1
                        print('spread', spread, 'prediction:', p, 'lost')

                #    print('yeet')
        except:
            continue
    print('won:', p_tally, 'lost:', vegas_tally)
    return [p_tally, vegas_tally]
            



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
      #  r = ratings[count*2+1]*-1
        pairs[r] = team
        totals.append(r)
        count += 1
    totals.sort()
    count = 0
    for t in totals:
        print(len(fb.teams)-count  ,t, pairs[t])
        count += 1


def stats_test():
    a = 0
    b = 0
    for i in range(9):
        print('nfl odds 20'+str(10+i)+'-'+str(11+i)+'.xlsx')
        load_file('nfl odds 20'+str(10+i)+'-'+str(11+i)+'.xlsx')
        get_teams()
        get_games()
        v = compare_vegas(1205)
        a += v[0]
        b += v[1]
    print(a/(a+b))
    
load_file(('excel files/nfl odds 2017-18.xlsx'))
get_teams()
get_games()

#print(len(fb.games))
compare_vegas(1196)
#print(len(fb.games))
#print(fb.games)
#r = fb.compute_ratings(0)
#fb.plot_ratings(r)
#rankings()
