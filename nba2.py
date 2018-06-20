import json

team_names = {}
player_names = {}

def read_teams():
    global teams
    f = open('nba_teams.json')
    x = json.loads(f.read())
    for t in x:
        id = t['teamId']
        name = t['simpleName']
        team_names[id] = name

def read_players():
    global players
    f = open('nba_players.json')
    x = json.loads(f.read())
    for p in x:
        id = p['playerId']
        name = p['firstName'] + ' ' + p['lastName']
        player_names[id] = name
        
read_players()
read_teams()
