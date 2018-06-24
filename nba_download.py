import urllib.request, urllib.parse

# download URL, write to file
#
def get_file(url, values, filename):
    data = urllib.parse.urlencode(values)
    data = data.encode('ascii')
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'}
    req = urllib.request.Request(url, data, headers)
    try:
        response = urllib.request.urlopen(req)
        f = open(filename, 'w')
        f.write(str(response.read()))
    except urllib.error.HTTPError as e:
        print(e.code)
        print(e.read())
        

for i in range(1200):
    i = str(i)
    id_len = len(i)
    id_len = 5-id_len
    id_string = '0' * id_len
    gameid = id_string + i
    url = 'http://data.nba.com/data/10s/v2015/json/mobile_teams/nba/2016/scores/pbp/00216'+ gameid + '_full_pbp.json'
    get_file(url, [], 'pbp' + gameid + '.json')
