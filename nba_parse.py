import json, copy

# return list of events in NBA JSON file
#
def read_json_file(name):
    f = open(name, 'r')
    x = json.loads(f.read())
    y = x['resultSets']
        # y has 2 elements
    z = y[0]
    a = z['rowSet']
    return a

def is_substitution(event):
    return event[2] == 8

def is_end_of_quarter(event):
    return event[2] == 13

teamid_0 = 0
teamid_1 = 0
team_name0 = ''
team_name1 = ''

def team_name(i):
    global team_name0, team_name1
    if i:
        return team_name1
    return team_name0

# for team rebounds, the data has a team ID in the player ID field (boo!)
#
def is_player_id(id):
    global teamid_0, teamid_1
    if not id:
        return False
    if id == teamid_0:
        return False
    if id == teamid_1:
        return False
    return True

player_names = {}

def player_name(id, name):
    global player_names;
    player_names[id] = name

# return list of players involved in event
#
def get_players(event):
    x = []
    if is_player_id(event[13]):
        x.append([event[13], event[15]])
        player_name(event[13], event[14])
    if is_player_id(event[20]):
        x.append([event[20], event[22]])
        player_name(event[20], event[21])
    if is_player_id(event[27]):
        x.append([event[27], event[29]])
        player_name(event[27], event[28])
    return x

# add player to current segment.
# if not already there, add to previous segments too
#
def add_player(player, team, seg, segs):
    if player in seg['players'][team]:
        return;
    seg['players'][team].append(player)
    for s in segs:
        s['players'][team].append(player)

def get_team(id):
    global teamid_0, teamid_1
    if id == teamid_0:
        return 0
    if id == teamid_1:
        return 1
    print('bad ID ', id);
    exit()

def new_segment(quarter):
    s = {}
    s['players'] = [[],[]]
    s['score'] = [None, None]
    s['time'] = [None, None]
    s['quarter'] = quarter
    return s

# return list of segments
# segment is a map
# players[2]: lists of players for each team
# time[2]: game time at start and end of segment
# score[2]: score at start and end of segment

def find_segments(events):
    global teamid_0, teamid_1, team_name0, team_name1
    quarter = 1
    print(len(events), ' events')
    teamid_0 = events[1][15]
    teamid_1 = events[1][22]
    team_name0 = events[1][18]
    team_name1 = events[1][25]
    segs_quarter = []       # list of segments in this quarter
    segs_game = []
    seg = new_segment(quarter)        # current segment
    for event in events:
        #print('event type ', event[2])
        if is_end_of_quarter(event):
            seg['time'][1] = event[6]
            segs_quarter.append(seg)
            quarter += 1
            seg = new_segment(quarter)
            segs_game.extend(segs_quarter)
            segs_quarter = []
        elif is_substitution(event):
            outgoing_player = event[13]
            incoming_player = event[20]
            player_name(event[13], event[14])
            player_name(event[20], event[21])
            team = get_team(event[15])
            add_player(outgoing_player, team, seg, segs_quarter)
            segs_quarter.append(copy.deepcopy(seg))
            seg['time'][0] = event[6]
            seg['score'][0] = copy.deepcopy(seg['score'][1])
            seg['players'][team].remove(outgoing_player)
            seg['players'][team].append(incoming_player)
        else:
            score = event[10]
            if score:
                if not seg['score'][0]:
                    seg['score'][0] = score
                seg['score'][1] = score
            time = event[6]
            if time:
                if not seg['time'][0]:
                    seg['time'][0] = time
                seg['time'][1] = time
            p = get_players(event)
            for x in p:
                if x[1] == None:
                    print(event)
                add_player(x[0], get_team(x[1]), seg, segs_quarter)
    out = []
    for seg in segs_game:
        if seg['time'][0] != seg['time'][1]:
            out.append(seg)
    return out

def print_segments(segs):
    global player_names
    n = 0
    for seg in segs:
        n += 1
        print('Segment ', n)
        print('   quarter: ', seg['quarter'])
        print('   start time: ', seg['time'][0])
        print('   end time: ', seg['time'][1])
        print('   start score: ', seg['score'][0])
        print('   end score: ', seg['score'][1])
        for i in range(2):
            print('  ', team_name(i), 'players:')
            for p in seg['players'][i]:
                print('      ', player_names[p])
            
events = read_json_file('nba_json.txt')
segs = find_segments(events)
print_segments(segs)
