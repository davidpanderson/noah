import math
import hash

def find_py(n):
    p = []
    for a in range(1, n):
        print('checking ', a)
        for b in range(a+1, int((a*a)/2)+1):
            h2 = a*a + b*b
            h = math.sqrt(h2)
            h = int(h + .5)
            if h*h == h2:
                p.append([a,b])
    return p

def remove_multiples(p, n):
    print('removing multiples')
    prime = []
    htsize = n
    hash_table = [[]]*htsize
    for py in p:
        #print('processing ',py)
        py_hash = hash.hash(py[0], py[1], htsize)
        #print('checking entry ', py_hash, hash_table[py_hash])
        if py in hash_table[py_hash]:
            #print('skipping')
            continue
        #print('appending ', py)
        prime.append(list(py))
        py_mult = list(py)
        while py_mult[0] < n:
            #print('in while: ', py_mult, n)
            h = hash.hash(py_mult[0], py_mult[1], htsize)
            hash_table[h].append(list(py_mult))
            #print('appending ', py_mult, ' in position ', h)
            py_mult[0] += py[0]
            py_mult[1] += py[1]
    return prime

def show_triples(ps):
    for p in ps:
        print(p[0], p[1], int(math.sqrt(p[0]*p[0]+p[1]*p[1])))

n = 500           
p = find_py(n)
#print(p)
p = remove_multiples(p, n)
#print(p)
show_triples(p)
