import json, copy, pickle

class nba:
    # IMPLEMENTATION STARTS HERE

    def __init__(self):
        self.segs = []
        self.player_names = {}    # map ID->name
        self.team_ids = {}        # IDs of 2 teams in current game
        self.team_names = {}
    
    # return list of events in NBA JSON file
    #
    def read_json_file(self, name):
        f = open(name, 'r')
        x = json.loads(f.read())
        y = x['resultSets']
            # y has 2 elements
        z = y[0]
        a = z['rowSet']
        return a

    def is_end_of_quarter(self, event):
        return event[2] == 13

    def is_substitution(self, event):
        return event[2] == 8

    # for team rebounds, the data has a team ID in the player ID field (boo!)
    #
    def is_player_id(self, id):
        if not id:
            return False
        if id == self.team_ids[0]:
            return False
        if id == self.team_ids[1]:
            return False
        return True

    # return list of players involved in event
    #
    def get_players(self, event):
        x = []
        if self.is_player_id(event[13]):
            x.append([event[13], event[15]])
            self.player_names[event[13]] = event[14]
        if self.is_player_id(event[20]):
            x.append([event[20], event[22]])
            self.player_names[event[20]] = event[21]
        if self.is_player_id(event[27]):
            x.append([event[27], event[29]])
            self.player_names[event[27]] = event[28]
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

    # take score as N - M and convert to list of 2 ints
    #
    def score_str_to_int(self, s):
        x = s.split("-")
        return [int(x[0]), int(x[1])]

    # take time as MM:SS and convert to seconds counting up
    #
    def time_str_to_secs(self, s):
        x = s.split(":")
        y = int(x[0])*60+int(x[1])
        return 720-y

    def time_secs_to_str(self, t):
        x = 720-t
        return "%d:%02d"%(x/60, x%60)

    # given list of events, return list of segments
    # segment is a map
    # quarter (1..4)
    # players[2]: lists of players for each team
    # time[2]: game time at start and end of segment (seconds from start of quarter)
    # score[2]: score at start and end of segment.  Each score is a pair of ints.

    def parse_game(self, filename):
        events = self.read_json_file(filename)
        quarter = 1
        print(len(events), ' events')
        print(self.team_ids)
        self.team_ids[0] = events[1][15]
        self.team_ids[1] = events[1][22]
        self.team_names[0] = events[1][18]
        self.team_names[1] = events[1][25]
        segs_quarter = []       # list of segments in this quarter
        segs_game = []
        seg = self.new_segment(quarter)        # current segment
        for event in events:
            #print('event type ', event[2])
            if self.is_end_of_quarter(event):
                seg['time'][1] = self.time_str_to_secs(event[6])
                segs_quarter.append(seg)
                quarter += 1
                seg = self.new_segment(quarter)
                segs_game.extend(segs_quarter)
                segs_quarter = []
            elif self.is_substitution(event):
                outgoing_player = event[13]
                incoming_player = event[20]
                self.player_names[event[13]] = event[14]
                self.player_names[event[20]] = event[21]
                team = self.get_team(event[15])
                self.add_player(outgoing_player, team, seg, segs_quarter)
                segs_quarter.append(copy.deepcopy(seg))
                seg['time'][0] = self.time_str_to_secs(event[6])
                seg['score'][0] = copy.deepcopy(seg['score'][1])
                seg['players'][team].remove(outgoing_player)
                seg['players'][team].append(incoming_player)
            else:
                score = event[10]
                if score:
                    s = self.score_str_to_int(score)
                    if not seg['score'][0]:
                        seg['score'][0] = s
                    seg['score'][1] = s
                time = event[6]
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
                print('  ', self.team_names[i], 'players:')
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
        
n = nba()
n.parse_game('nba_json.txt')
#n.print_segments()
n.write_data("foo")
