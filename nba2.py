# main program for NBA player analysis.
# - read data from game files
# - divide into segments (periods w/ same 10 players)
# - do optimization to find player coefficients
# - show results

import json, copy, pickle, os, random
import numpy as np
from scipy.optimize import minimize
import nba_analyze
from itertools import combinations

# URLs
# players: http://data.nba.net/data/10s/prod/v1/2017/players.json
# teams: http://data.nba.net/data/10s/prod/v1/2017/teams.json
# schedule: http://data.nba.net/data/10s/prod/v1/2017/schedule.json
# games: see nba_download.py

# A source of CSV game data: https://eightthirtyfour.com/data

# Note: Firefox will let you browse a .json file

def off(r):
    return r[1]

def defense(r):
    return r[2]

def ovr(r):
    return r[1] - r[2]

class NBA:
    # IMPLEMENTATION STARTS HERE

    # A segment is a map
    # quarter (1..4)
    # players[2]: lists of players for each team
    # time[2]: game time at start and end of segment (seconds from start of quarter)
    # score[2]: score at start and end of segment.  Each score is a pair of ints.

    def __init__(self):
        self.segs = []
        self.player_names = {}      # map ID->name
        self.team_ids = {}          # IDs of 2 teams in current game
        self.team_names = {}        # map ID->name
        self.trimmed_segs = []
        self.player_seqno = {}       # map ID->seqno
            # we need seqnos for players since optimization takes an array

    # map player ID to name
    # NOTE: the player lists are incomplete, maybe for players on short contracts
    #
    def player_name(self, player_id):
        if player_id in self.player_names:
            return self.player_names[player_id]
        return 'Unknown'
    
    # print list of player IDs as names
    #
    def print_players(self, players):
        for id in players:
            print(self.player_name(id))
        
    # get team names; make map
    #
    def read_teams(self):
        global teams
        f = open('nba_data/teams.json')
        x = json.loads(f.read())
        for t in x:
            id = t['teamId']
            name = t['simpleName']
            self.team_names[id] = name

    # get player names
    #
    def read_players(self, filename):
        global players
        f = open(filename)
        x = json.loads(f.read())
        x = x['league']
        x = x['standard']
        for p in x:
            id = int(p['personId'])
            name = p['firstName'] + ' ' + p['lastName']
            self.player_names[id] = name

    # return list of events in NBA JSON file
    # events are things like baskets, player substitutions, etc.
    # In the data file these are divided into "period"
    #
    def read_game(self, name):
      #  print('reading game ', name)
        f = open(name)
        x = f.read()
        if x[:2] == "b'":
            x = x[2:-1]
        x = x.encode('latin1').decode('unicode-escape').encode('latin1').decode('utf-8')
        x = json.loads(x)
        x = x['g']
        periods = x['pd']
        e = []
        #print(len(periods), ' periods')
        for i in range(len(periods)):
            x = periods[i]
            e.extend(x['pla'])
        return e

    def is_end_of_quarter(self, event):
        return int(event['etype']) == 13

    def is_substitution(self, event):
        return int(event['etype']) == 8

    def is_technical_foul(self, event):
        if int(event['etype']) == 11:
            # player ejection (can be on bench)
            return True
        if int(event['etype']) != 6:
            return False
        return 'Technical' in event['de']

    # return list of players involved in event
    # return list of (playerid, teamid) pairs
    #
    def get_players(self, event):
        x = []
        t1 = int(event['tid'])      # team ID
        t2 = int(event['oftid'])
        p = int(event['pid'])
        if (p in self.player_names):
            x.append([p, t1])
        if (event['epid']):
            p = int(event['epid'])
            if (p in self.player_names):
                if (event['etype'] != 10):
                    # for jump ball the 2nd player could be on either team
                    x.append([p, t1])
        return x

    # return true if each segment is 5 on 5
    #
    def check_segs(self, segs):
         for seg in segs:
             for i in range(2):
                 n = len(seg['players'][i])
                 if  n != 5:
                       # print("bad # players in check_segs: ", n)
                        #print(seg)
                        return False
                        #exit()
         return True
                    
    # add player to current segment.
    # if not already there, add to previous segments too
    #
    def add_player(self, player, team, seg, segs):
        if player in seg['players'][team]:
            return;
        #print('adding ', player, self.player_name(player), team)
        #self.print_players(seg['players'][team])
        if len(seg['players'][team]) >= 5:
            print("bad # players in add_player");
            print(seg)
            return
        seg['players'][team].append(player)

        for s in segs:
            s['players'][team].append(player)

    def get_team(self, id):
        if id == self.team_ids[0]:
            return 0
        if id == self.team_ids[1]:
            return 1
        print('bad ID ', id, self.team_ids);
        exit()

    def new_segment(self, quarter):
        #print('new segment')
        s = {}
        s['players'] = [[],[]]
        s['score'] = [[], []]
        s['time'] = [-1, -1]
        s['quarter'] = quarter
        return s

    # take time as MM:SS and convert to seconds counting up
    #
    def time_str_to_secs(self, s):
        x = s.split(":")
        y = float(x[0])*60+float(x[1])
        return 720-y

    def time_secs_to_str(self, t):
        x = 720-t
        x = int(x)
        return "%d:%02d"%(x/60, x%60)

    # parse a game file; append list of segments to self.segs
    #
    def parse_game(self, filename):
        events = self.read_game(filename)
        quarter = 1

        # find the team IDs, in the order used for scores (home, visitor)

        tid0 = 0
        tid1 = 0
        for event in events:
            if event['hs']:
                tid0 = event['tid']
                break
        for event in events:
            if event['vs']:
                tid1 = event['tid']
                break
        self.team_ids = [tid0, tid1]

        #print('parsing game '+filename)
      #  print('between '+self.team_names[tid0]+' and '+self.team_names[tid1])
        #print(len(events), ' events')
        segs_quarter = []       # list of segments in this quarter
        segs_game = []
        seg = self.new_segment(quarter)        # current segment
        for event in events:
            #print('event ', event['evt'], ' type ', event['etype'], event['de'])
            if event['etype'] == 10:
                # jump ball.  sometimes data is bad
                continue
            if self.is_end_of_quarter(event):
                # some game files erroneously have two End Periods in a row
                if not segs_quarter:
                    continue
                seg['time'][1] = self.time_str_to_secs(event['cl'])
                segs_quarter.append(seg)
                quarter += 1
                seg = self.new_segment(quarter)
                if self.check_segs(segs_quarter):
                    segs_game.extend(segs_quarter)
                segs_quarter = []
            elif self.is_substitution(event):
                outgoing_player = int(event['pid'])
                incoming_player = int(event['epid'])
                team = self.get_team(event['tid'])
                self.add_player(outgoing_player, team, seg, segs_quarter)
                segs_quarter.append(copy.deepcopy(seg))
                seg['time'][0] = self.time_str_to_secs(event['cl'])
                seg['score'][0] = copy.deepcopy(seg['score'][1])
                seg['players'][team].remove(outgoing_player)
                seg['players'][team].append(incoming_player)
            elif self.is_technical_foul(event):
                # technical foul can involve someone on bench
                continue
            else:
                s = []
                s.append(event['hs'])
                s.append(event['vs'])
                if not seg['score'][0]:
                    seg['score'][0] = s
                seg['score'][1] = s
                time = event['cl']
                if time:
                    if seg['time'][0] < 0:
                        seg['time'][0] = self.time_str_to_secs(time)
                    seg['time'][1] = self.time_str_to_secs(time)
                p = self.get_players(event)
                for x in p:
                   # if x[1] == None:
                      #  print(event)
                      
                    self.add_player(x[0], self.get_team(x[1]), seg, segs_quarter)

        # append this game's segments to self.segs
        #
        for seg in segs_game:
            if seg['time'][0] != seg['time'][1]:
                seg['duration'] = seg['time'][1] - seg['time'][0]
                seg['points_scored'] = [0,0]
                for i in range(2):
                    seg['points_scored'][i] = seg['score'][1][i] - seg['score'][0][i]
                self.segs.append(seg)

    # return avg off and def ratings of a group of players
    #
    def rating_avgs(self, players):
        osum = 0
        dsum = 0
        for pid in players:
            pseq = self.player_seqno[pid]
            osum += self.player_ratings[2*pseq]
            dsum += self.player_ratings[2*pseq+1]
        return [osum/5, dsum/5]

    # print predicted score for a segment, based on who's playing
    #
    def print_predictions(self, seg, ta):
        tb = 1 - ta
        ra = self.rating_avgs(seg['players'][ta])
        rb = self.rating_avgs(seg['players'][tb])
        print('     average rating: ', ra)
        pred = ra[0]*rb[1]*seg['duration']
        print('     predicted points scored: ', pred)
        
    def print_segments(self):
        n = 0
        for seg in self.segs:
            n += 1
            print('Segment ', n)
            print('   quarter: ', seg['quarter'])
            print('   start time: ', self.time_secs_to_str(seg['time'][0]))
            print('   end time: ', self.time_secs_to_str(seg['time'][1]))
            print('   duration: ', seg['duration'])
            s = seg['score'][0]
            print('   start score: %d - %d'%(s[0], s[1]))
            s = seg['score'][1]
            print('   end score: %d - %d'%(s[0], s[1]))
            print('   points scored: ', seg['points_scored'])
            for i in range(2):
                print('  ', self.team_names[self.team_ids[i]])
                for p in seg['players'][i]:
                    if len(self.player_ratings):
                        pseq = self.player_seqno[p]
                        offr = self.player_ratings[pseq*2]
                        defr = self.player_ratings[pseq*2+1]
                        print('     ', self.player_name(p), offr, defr)
                    else:
                        print('      ', self.player_name(p))
                if len(self.player_ratings):
                   self.print_predictions(seg, i)

    def write_data(self, filename):
        pickle.dump(self, open(filename, 'wb'))

    def read_data(self, filename):
        x = pickle.load(open(filename, 'rb'))
        self.segs = x.segs
        self.player_names = x.player_names
        self.team_names = x.team_names
        self.team_ids = x.team_ids

    # given a set of segments, find ratings for players such that
    # predicted scores are as close as possible to actual scores
    #
    def analyze(self):
        # trim segment list, and assign seq nos to players

        seqno = 0
        for seg in self.segs:
            dur = seg['time'][1] - seg['time'][0]
            if (dur < 0):
                continue
            self.trimmed_segs.append(seg)
            for i in range(2):
                for p in seg['players'][i]:
                    if p not in self.player_seqno:
                        self.player_seqno[p] = seqno
                        seqno += 1
        ratings = []
        for i in range(seqno):
            ratings.append(0.03)
            ratings.append(1.0)
        x0 = np.array(ratings)
        # list of available methods is here:
        # https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.minimize.html
        # Newton-CG hangs in some cases;SLSQP seems to work
        res = minimize(nba_analyze.nba_error,x0, jac=nba_analyze.nba_error_gradient,
            method='SLSQP',tol=1e-9, options={'maxiter': 1e8, 'disp': True})
        self.player_ratings = res.x

            
    def average_offr(self):
        total = 0
        n = 0
        for id, seqno in self.player_seqno.items():
            offr = self.player_ratings[2*seqno]
            total += offr
            n += 1
        print(total/n)
        return total/n

    def print_leaders(self, r, func, title, numplayers):
        print(title)
        i = 1
        for p in r:
            print(i, p[0], func(p))
            i += 1
            if i> numplayers:
                return
            
    def print_ratings(self, numplayers, min_dur):
        a_offr = self.average_offr()
        x = []
        player_stats = self.compute_player_stats()
        for id, seqno in self.player_seqno.items():
            if player_stats[id]['dur'] < min_dur:
                continue
            offr = self.player_ratings[2*seqno]
            offr = offr/a_offr
            defr = self.player_ratings[2*seqno+1]
            x.append([self.player_name(id), offr, defr])
                
            # print(self.player_name(id),  offr , defr, offr - defr )
        print(x)
        x.sort(key=off, reverse=True)
        self.print_leaders(x, off, 'offensive rating', numplayers)
        x.sort(key=defense)
        self.print_leaders(x, defense, 'defensive rating', numplayers)
        x.sort(key=ovr, reverse=True)
        self.print_leaders(x, ovr, 'overall rating', numplayers)
         
    def save(self, year, tag):
        f = open('nba_results/nba_%d_%d.pickle'%(year, tag), 'wb')
        pickle.dump(self, f)
        f.close()

    def restore(self, year, tag):
        f = open('nba_results/nba_%d_%d.pickle'%(year, tag), 'rb')
        x = pickle.load(f)
        self.segs = x.segs
        self.player_names = x.player_names
        self.team_names = x.team_names
        self.team_ids = x.team_ids
        self.player_seqno = x.player_seqno
        self.player_ratings = x.player_ratings
        self.trimmed_segs = x.trimmed_segs
        f.close()

    # for each player, show
    # # of segments
    # duration of segments
    # points scored by team and by other team
    #
    def compute_player_stats(self):
        players = {}
        for seg in self.segs:
            dur = seg['duration']
            for ta in range(2):
                tb = 1 - ta
                pa = seg['points_scored'][ta]
                pb = seg['points_scored'][tb]
                for p in seg['players'][ta]:
                    if  p not in players:
                        x = {}
                        x['nsegs'] = 0
                        x['dur'] = 0
                        x['pf'] = 0
                        x['pa'] = 0
                        players[p] = x
                    players[p]['nsegs'] += 1
                    players[p]['dur'] += dur
                    players[p]['pf'] += pa
                    players[p]['pa'] += pb
        return players

    def trim_segments(self, min_dur):
        stats = self.compute_player_stats()
    #    print(stats)
        for seg in self.segs:
            v = 0
            for t in seg['players']:
                for p in t:
                    player = stats[p]
                    if player['dur'] < min_dur:
                        v = 1
                        break
            if v == 1:
                self.segs.remove(seg)
        
        return players
    
    def print_player_stats(self, players):
        for pid, x in players.items():
            print("%s: n %d dur %d pf %d pa %d pts %f"%(self.player_name(pid), x['nsegs'], x['dur'], x['pf'], x['pa'], (x['pf'] + x['pa'])/x['dur']))
    
    def print_player_stats(self, players):
        for pid, x in players.items():
            print("%s: n %d dur %d pf %d pa %d pts %f"%(self.player_name(pid), x['nsegs'], x['dur'], x['pf'], x['pa'], (x['pf'] + x['pa'])/x['dur']))
    
# given list of teams, return list of games between any two of them
#
def game_find(year, teams):
    x = []
    f = open('nba_data/'+year+'/schedule.json')
    games = json.loads(f.read())
    games = games['league']
    games = games['standard']
    for g in games:
        hteam = g['hTeam']
        vteam = g['vTeam']
        hteam = hteam['teamId']
        vteam = vteam['teamId']
        if hteam not in teams:
            continue
        if vteam not in teams:
            continue
        x.append(g['gameId'+ '.json'])
    return x


def find_all_games(year):
    dirname = 'nba_data/%d/games'%(year)
    files = os.listdir(dirname)
    games= []
    for file in files:
        #1 is preaseason, 2 is regular season, 3 is all star game, 4 is playoffs
        if file[2] == '1':
            continue
        if file[2] == '3':
            continue
        games.append(file)
    return games
        
def analyze_games(year, game_ids, tag=''):
    nba_analyze.nba = NBA()
    nba_analyze.nba.read_players('nba_data/2017/players.json')
    nba_analyze.nba.read_players('nba_data/2016/players.json')
    nba_analyze.nba.read_players('nba_data/2018/players.json')
    nba_analyze.nba.read_teams()
    #nba_analyze.nba.parse_game('nba_data/2018/games/0021800388.json')

    for id in game_ids:
        f = 'nba_data/%d/games/%s'%(year, id)
        #print(f)
        nba_analyze.nba.parse_game(f)
    print(len(nba_analyze.nba.segs))
    nba_analyze.nba.trim_segments(72000)
    print(len(nba_analyze.nba.segs))
    return
    nba_analyze.nba.analyze()
    #nba_analyze.nba.print_segments()
    #nba_analyze.nba.average_offr()
    nba_analyze.nba.save(year, tag)

def print_info(year, tag, nplayers, min_dur):
    nba_analyze.nba = NBA()
    nba_analyze.nba.restore(year, tag)
    nba_analyze.nba.print_ratings(nplayers, min_dur)
  #  players = nba_analyze.nba.compute_player_stats()
    #nba_analyze.nba.print_player_stats(players)

def split_list(g):
    random.shuffle(g)
    n = len(g)//2
    return [g[:n], g[n:]]

def analyze_halves(year):
    games = find_all_games(year)
    (g1, g2) = split_list(games)
    analyze_games(year, g1, '_1')
    print("first half done")
    analyze_games(year, g2, '_2')


def split_list(g):
    random.shuffle(g)
    n = len(g)//2
    return [g[:n], g[n:]]

def analyze_halves(year):
    games = find_all_games(year)
    (g1, g2) = split_list(games)
    analyze_games(year, g1, '_1')
    print("first half done")
    analyze_games(year, g2, '_2')

#games = ['0041700401', '0041700402', '0041700403', '0041700404']
#games = game_find('2018', ['1610612757', '1610612740', '1610612744', '1610612759', '1610612747',  '1610612746'])
#games = game_find('2018', ['1610612757', '1610612740'])
games = find_all_games(2017)
#games = find_all_games(2017)
#analyze_games(2017, games)
print_info(2017, 1, 50, 30000)
print_info(2017, 2, 50, 30000)

analyze_games(2017, games)
#print_info(2017, 1, 50, 30000)
#print_info(2017, 2, 50, 30000)

#analyze_halves(2017)
