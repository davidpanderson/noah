import json, copy, pickle, os

# URLs
# players: http://data.nba.net/data/10s/prod/v1/2017/players.json
# teams: http://data.nba.net/data/10s/prod/v1/2017/teams.json
# schedule: http://data.nba.net/data/10s/prod/v1/2017/schedule.json

class nba:
    # IMPLEMENTATION STARTS HERE

    def __init__(self):
        self.segs = []
        self.player_names = {}      # map ID->name
        self.team_ids = {}          # IDs of 2 teams in current game
        self.team_names = {}        # map ID->name
    
    def read_teams(self):
        global teams
        f = open('nba_teams.json')
        x = json.loads(f.read())
        for t in x:
            id = t['teamId']
            name = t['simpleName']
            self.team_names[id] = name

    def read_players(self):
        global players
        f = open('nba_players_2015.json')
        x = json.loads(f.read())
        x = x['league']
        x = x['standard']
        for p in x:
            id = int(p['personId'])
            name = p['firstName'] + ' ' + p['lastName']
            self.player_names[id] = name

    # return list of events in NBA JSON file
    #
    def read_game(self, name):
        f = open(name)
        x = json.loads(f.read())
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
        t1 = int(event['tid'])
        t2 = int(event['oftid'])
        p = int(event['pid'])
        if (p in self.player_names):
            x.append([p, t1])
        if (event['epid']):
            p = int(event['epid'])
            if (p in self.player_names):
                if (event['etype'] == 10):
                    x.append([p, t2])
                else:
                    x.append([p, t1])
        return x

    # add player to current segment.
    # if not already there, add to previous segments too
    #
    def add_player(seld, player, team, seg, segs):
        if player in seg['players'][team]:
            return;
        seg['players'][team].append(player)
        for s in segs:
            s['players'][team].append(player)

    def get_team(self, id):
        if id == self.team_ids[0]:
            return 0
        if id == self.team_ids[1]:
            return 1
        print('bad ID ', id);
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

    # given list of events, return list of segments
    # segment is a map
    # quarter (1..4)
    # players[2]: lists of players for each team
    # time[2]: game time at start and end of segment (seconds from start of quarter)
    # score[2]: score at start and end of segment.  Each score is a pair of ints.

    def parse_game(self, filename):
        events = self.read_game(filename)
        quarter = 1
        print(len(events), ' events')
        self.team_ids[0] = events[1]['tid']
        self.team_ids[1] = events[1]['oftid']
        segs_quarter = []       # list of segments in this quarter
        segs_game = []
        seg = self.new_segment(quarter)        # current segment
        for event in events:
            #print('event type ', event['etype'])
            if self.is_end_of_quarter(event):
                seg['time'][1] = self.time_str_to_secs(event['cl'])
                segs_quarter.append(seg)
                quarter += 1
                seg = self.new_segment(quarter)
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
        
        for seg in segs_game:
            if seg['time'][0] != seg['time'][1]:
                self.segs.append(seg)

    def print_segments(self):
        n = 0
        for seg in self.segs:
            n += 1
            print('Segment ', n)
            print('   quarter: ', seg['quarter'])
            print('   start time: ', self.time_secs_to_str(seg['time'][0]))
            print('   end time: ', self.time_secs_to_str(seg['time'][1]))
            s = seg['score'][0]
            print('   start score: %d - %d'%(s[0], s[1]))
            s = seg['score'][1]
            print('   end score: %d - %d'%(s[0], s[1]))
            for i in range(2):
                print('  ', self.team_names[self.team_ids[i]], 'players:')
                for p in seg['players'][i]:
                    print('      ', self.player_names[p])

    def write_data(self, filename):
        pickle.dump(self, open(filename, 'wb'))

    def read_data(self, filename):
        x = pickle.load(open(filename, 'rb'))
        self.segs = x.segs
        self.player_names = x.player_names
        self.team_names = x.team_names
        self.team_ids = x.team_ids

    def analyze(self):
        # trim segment list, and assign seq nos to players

        trimmed_segs = []
        player_seqno = {}
        seqno = 0
        for seg in self.segs:
            dur = seg['time'][1] - seg['time'][0]
            if (dur < 0):
                continue
            trimmed_segs.append(seg)
            for i in range(2):
                for p in seg['players'][i]:
                    if p not in player_seqno:
                        player_seqno[p] = seqno
                        seqno += 1
        res = minimize(nba_score_error,x0, jac=nba_score_error_gradient,
            tol=1e-7, options={'maxiter': 1e8, 'disp': True})
        player_ratings = res.x

    def parse_games(self, year):
        dirname = 'nba_games_%d'%(year)
        files = os.listdir(dirname)
        for file in files:
            if file[2] == '1':
                continue
            self.parse_game('%s/%s'%(dirname, file))
            
def nba_test():   
    n = nba()
    n.read_players()
    n.read_teams()
    n.parse_games(2017)
    #n.parse_game('0021600361_full_pbp.json')
    #n.print_segments()
    #n.write_data("foo")

nba_test()
