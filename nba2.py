# main program for NBA player analysis.
# - read data from game files
# - divide into segments (periods w/ same 10 players)
# - do optimization to find player coefficients
# - show results

import json, copy, pickle, os
import numpy as np
from scipy.optimize import minimize
import nba_analyze
from itertools import combinations

# URLs
# players: http://data.nba.net/data/10s/prod/v1/2017/players.json
# teams: http://data.nba.net/data/10s/prod/v1/2017/teams.json
# schedule: http://data.nba.net/data/10s/prod/v1/2017/schedule.json

# Note: Firefox will let you browse a .json file

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

    # print list of IDs as names
    #
    def print_players(self, players):
        for id in players:
            print(self.player_names[id])
        
    # get team names; make map
    #
    def read_teams(self):
        global teams
        f = open('nba_teams.json')
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
        f = open(name)
        x = f.read()
        if x[:2] == "b'":
            x = x[2:-1]
        x = json.loads(x)
        x = x['g']
        periods = x['pd']
        e = []
        print(len(periods), ' periods')
        for i in range(len(periods)):
            x = periods[i]
            e.extend(x['pla'])
        return e

    def is_end_of_quarter(self, event):
        return int(event['etype']) == 13

    def is_substitution(self, event):
        return int(event['etype']) == 8

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

    # verify that each segment is 5 on 5
    #
    def check_segs(self, segs):
         for seg in segs:
             for i in range(2):
                 if len(seg['players'][i]) != 5:
                        print("bad # players")
                        print(seg)
                        exit()
                    
    # add player to current segment.
    # if not already there, add to previous segments too
    #
    def add_player(self, player, team, seg, segs):
        if player in seg['players'][team]:
            return;
        #print('adding ', self.player_names[player], team)
        seg['players'][team].append(player)
        #self.print_players(seg['players'][team])
        if len(seg['players'][team]) > 5:
            print("bad # players");
            print(seg)
            exit()
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

    # parse a game file; return list of segments
    #
    def parse_game(self, filename):
        events = self.read_game(filename)
        quarter = 1
        print(len(events), ' events')

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
        
        segs_quarter = []       # list of segments in this quarter
        segs_game = []
        seg = self.new_segment(quarter)        # current segment
        for event in events:
            #print('event ', event['evt'], ' type ', event['etype'])
            if self.is_end_of_quarter(event):
                seg['time'][1] = self.time_str_to_secs(event['cl'])
                segs_quarter.append(seg)
                quarter += 1
                seg = self.new_segment(quarter)
                self.check_segs(segs_quarter)
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
            elif event['etype'] == 6:
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
                    if x[1] == None:
                        print(event)
                    self.add_player(x[0], self.get_team(x[1]), seg, segs_quarter)

        # what does the following do?
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
                        print('     ', self.player_names[p], offr, defr)
                    else:
                        print('      ', self.player_names[p])
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
        res = minimize(nba_analyze.nba_error,x0, jac=nba_analyze.nba_error_gradient,
            method='Newton-CG',tol=1e-9, options={'maxiter': 1e8, 'disp': True})
        self.player_ratings = res.x

    def parse_games(self, year):
        dirname = 'nba_games_%d'%(year)
        files = os.listdir(dirname)
        for file in files:
            if file[2] == '1':
                continue
            self.parse_game('%s/%s'%(dirname, file))
    def average_offr(self):
        total = 0
        n = 0
        for id, seqno in self.player_seqno.items():
            offr = self.player_ratings[2*seqno]
            total += offr
            n += 1
        print(total/n)
        return total/n

    def print_ratings(self):
        a_offr = self.average_offr()
        for id, seqno in self.player_seqno.items():
            offr = self.player_ratings[2*seqno]
            offr = offr/a_offr
            defr = self.player_ratings[2*seqno+1]
            print(self.player_names[id],  offr , defr, offr - defr )

    # for each player, show
    # # of segments
    # duration of segments
    # points scored by team and by other team
    #
    def print_stats(self):
        players = {}
        for seg in self.trimmed_segs:
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
        for pid, x in players.items():
            print("%s: n %d dur %d pf %d pa %d"%(self.player_names[pid], x['nsegs'], x['dur'], x['pf'], x['pa']))

    
        

# given two teams, return list of games between them
#
def game_find(teams):
    x = []
    f = open('nba_schedule_2017.json')
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
        x.append(g['gameId'])
    print(x)
    return x
    
def nba_test(game_ids):
    nba_analyze.nba = NBA()
    nba_analyze.nba.read_players('nba_players_2017.json')
    nba_analyze.nba.read_players('nba_players_2016.json')

    nba_analyze.nba.read_teams()
    #nba.parse_games(2017)
    for id in game_ids:
        f = 'nba_games_2017/'+id+'.json'
        print(f)
        nba_analyze.nba.parse_game(f)
    nba_analyze.nba.analyze()
    #nba_analyze.nba.print_segments()
    #nba_analyze.nba.average_offr()
    #nba.write_data("foo")
    nba_analyze.nba.print_ratings()
    nba_analyze.nba.print_stats()
    nba_analyze.nba.average_offr()


#games = ['0041700401', '0041700402', '0041700403', '0041700404']
games = game_find(['1610612757', '1610612740', '1610612744'])
nba_test(games)



