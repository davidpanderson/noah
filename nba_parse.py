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

# for team rebounds, the data has a team ID in the player ID field (boo!)
#
def is_player_id(id, team_ids):
    if not id:
        return False
    if id == team_ids[0]:
        return False
    if id == team_ids[1]:
        return False
    return True

# return list of players involved in event
#
def get_players(event, team_ids, player_names):
    x = []
    if is_player_id(event[13], team_ids):
        x.append([event[13], event[15]])
        player_names[event[13]] = event[14]
    if is_player_id(event[20], team_ids):
        x.append([event[20], event[22]])
        player_names[event[20]] = event[21]
    if is_player_id(event[27], team_ids):
        x.append([event[27], event[29]])
        player_names[event[27]] = event[28]
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

def get_team(id, team_ids):
    if id == team_ids[0]:
        return 0
    if id == team_ids[1]:
        return 1
    print('bad ID ', id);
    exit()

def new_segment(quarter):
    s = {}
    s['players'] = [[],[]]
    s['score'] = [[], []]
    s['time'] = [-1, -1]
    s['quarter'] = quarter
    return s

# take score as N - M and convert to list of 2 ints
#
def score_str_to_int(s):
    x = s.split("-")
    return [int(x[0]), int(x[1])]

# take time as MM:SS and convert to seconds counting up
#
def time_str_to_secs(s):
    x = s.split(":")
    y = int(x[0])*60+int(x[1])
    return 720-y

def time_secs_to_str(t):
    x = 720-t
    return "%d:%02d"%(x/60, x%60)

# return list of segments
# segment is a map
# quarter (1..4)
# players[2]: lists of players for each team
# time[2]: game time at start and end of segment (seconds from start of quarter)
# score[2]: score at start and end of segment.  Each score is a pair of ints.

def find_segments(events):
    quarter = 1
    print(len(events), ' events')
    team_ids = {}
    team_ids[0] = events[1][15]
    team_ids[1] = events[1][22]
    team_names = {}
    team_names[0] = events[1][18]
    team_names[1] = events[1][25]
    player_names = {}
    segs_quarter = []       # list of segments in this quarter
    segs_game = []
    seg = new_segment(quarter)        # current segment
    for event in events:
        #print('event type ', event[2])
        if is_end_of_quarter(event):
            seg['time'][1] = time_str_to_secs(event[6])
            segs_quarter.append(seg)
            quarter += 1
            seg = new_segment(quarter)
            segs_game.extend(segs_quarter)
            segs_quarter = []
        elif is_substitution(event):
            outgoing_player = event[13]
            incoming_player = event[20]
            player_names[event[13]] = event[14]
            player_names[event[20]] = event[21]
            team = get_team(event[15], team_ids)
            add_player(outgoing_player, team, seg, segs_quarter)
            segs_quarter.append(copy.deepcopy(seg))
            seg['time'][0] = time_str_to_secs(event[6])
            seg['score'][0] = copy.deepcopy(seg['score'][1])
            seg['players'][team].remove(outgoing_player)
            seg['players'][team].append(incoming_player)
        else:
            score = event[10]
            if score:
                s = score_str_to_int(score)
                if not seg['score'][0]:
                    seg['score'][0] = s
                seg['score'][1] = s
            time = event[6]
            if time:
                if seg['time'][0] < 0:
                    seg['time'][0] = time_str_to_secs(time)
                seg['time'][1] = time_str_to_secs(time)
            p = get_players(event, team_ids, player_names)
            for x in p:
                if x[1] == None:
                    print(event)
                add_player(x[0], get_team(x[1], team_ids), seg, segs_quarter)
    out = []
    for seg in segs_game:
        if seg['time'][0] != seg['time'][1]:
            out.append(seg)
    return [out, team_names, player_names]

def print_segments(segs, team_names, player_names):
    n = 0
    for seg in segs:
        n += 1
        print('Segment ', n)
        print('   quarter: ', seg['quarter'])
        print('   start time: ', time_secs_to_str(seg['time'][0]))
        print('   end time: ', time_secs_to_str(seg['time'][1]))
        s = seg['score'][0]
        print('   start score: %d - %d'%(s[0], s[1]))
        s = seg['score'][1]
        print('   end score: %d - %d'%(s[0], s[1]))
        for i in range(2):
            print('  ', team_names[i], 'players:')
            for p in seg['players'][i]:
                print('      ', player_names[p])
            
events = read_json_file('nba_json.txt')
x = find_segments(events)
print_segments(x[0], x[1], x[2])
