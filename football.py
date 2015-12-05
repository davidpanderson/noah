def r():
    w = []
    f = open('ncaa_football.txt', 'r')
    for line in f:
        line = line.strip()
        if line != '':
            w.append(line)
    return w

def teams():
    t = []
    f = r()
    for l in f:
        x = True
        try:
            int(l[0])
        except:
            x = False
            
        if x == False:
            l = l.split(' (')
            t.append(l[0])
    return t

#ts = teams()            
#for t in ts:
#    print(t)
   
def int_check(c):
    try:
        int(c)
    except:
        return False
    return True


def games():
    t = teams()
    g = []
    f = r()
    for line in f:
        words = line.split('\t')
        if len(words) >= 7:
            t2 = words[3].replace('*', '')
            if t1 < t2:
                d = [t1, t2, words[5], words[6]]
                g.append(d)
        else:
             words = line.split(' (')
             t1 = words[0]
    return g

g = games()
print(g)
print(len(g))
                
                


 
    
