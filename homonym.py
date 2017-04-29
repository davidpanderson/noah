from collections import defaultdict

# read word/pronunciation list
#
def read_list():
    list = []
    f = open("pronounce.txt", "r")
    while True:
        line = f.readline()
        line = line.strip()
        if len(line) == 0:
            break
        line = line.lower()
        x = line.split("  ")
        list.append([x[0], x[1]])
    return list
        
# read word/pronunciation list, make map of pronunciation to word list
#
def pronounce_map():
    map = defaultdict(list)
    f = open("pronounce.txt", "r")
    while True:
        line = f.readline()
        line = line.strip()
        if len(line) == 0:
            break
        line = line.lower()
        x = line.split("  ")
        map[x[1]].append(x[0])
    return map

def homonyms(n):
    map = pronounce_map()
    for p in map:
        words = map[p]
        if len(words) >= n:
            print words

def palindromes():
    list = read_list()
    for x in list:
        p = x[1]
        q = p.split(" ")
        r = q[::-1]
        #print q, r
        if q == r:
            print x[0], x[1]
    
#homonyms(5)

palindromes()
