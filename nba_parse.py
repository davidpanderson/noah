import json

f = open('nba_json.txt', 'r')
x = f.read()
x = json.loads(x)
y = x['resultSets']
print(len(y))
z = y[0]
a = z['rowSet']
print(len(a))
for i in range(10):
    print(a[i])
