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
        
data={}
data['EndPeriod']=10
data['EndRange']=55800
data['GameID']='0021700001'
data['RangeType']=2
data['Season']='2015-16'
data['SeasonType']='Regular Season'
data['StartPeriod']=1
get_file('http://stats.nba.com/stats/playbyplayv2', data, 'foo')
