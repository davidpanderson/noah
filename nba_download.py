import os, json, urllib.request, urllib.parse

def parse_schedule(year):
    ids = []
    f = open('nba_data/%d/schedule.json'%(year))
    x = json.loads(f.read())
    x = x['league']
    x = x['standard']
    for g in x:
        ids.append(g['gameId'])
    return ids
    
# download URL, write to file
#
def get_file(url, filename):
    req = urllib.request.Request(url)
    try:
        response = urllib.request.urlopen(req)
        f = open(filename, 'w')
        f.write(str(response.read()))
    except urllib.error.HTTPError as e:
        print(e.code)
        print(e.read())

def download_games(year):
    game_ids = parse_schedule(year)
    for game_id in game_ids:
        url = 'http://data.nba.com/data/10s/v2015/json/mobile_teams/nba/%d/scores/pbp/%s_full_pbp.json'%(year, game_id)
        file = 'nba_data/%d/games/%s.json'%(year, game_id)
        if (os.path.exists(file)):
            print (file, ' already exists')
            continue
        print (url)
        get_file(url, file)

download_games(2018)
