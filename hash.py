
def hash(i, j, htsize):
    return int(str(i)+str(j)) % htsize

def hash_test():
    htsize = 50
    table = [0]*htsize
    ncollisions = 0
    for i in range(1, 100):
        for j in range(1, 100):
            h = hash(i,j, htsize)
            ncollisions += table[h]
            table[h] += 1
    print(ncollisions/10000)

#hash_test()
