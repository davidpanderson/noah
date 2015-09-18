import math

# return a list of Booleans for 0..n-1
# where True means prime and False means not prime
#
def prime_sieve(n):
    p = []
    for i in range(n):
        p.append(True)
    s = int((math.ceil(math.sqrt(n))))
    for i in range(2, s):
        j = i
        while True:
            j = j + i
            if (j >= n): break
            p[j] = False
    return p

# return a list of the prime numbers less than n
#
def prime_numbers(n):
    x = prime_sieve(n)
    p = []
    for i in range(2, n):
        if x[i]:
            p.append(i)
    return p

# return a list of the prime factors of n,
# in increasing order
#
def prime_factors(n):
    r = []
    m = prime_numbers(n+1)
    i = 0
    while n > 1:
        f = m[i]
        if n % f == 0:
            r.append(f)
            n = n/f
        else:
            i = i + 1
    return r
            
                
                
            
    
       
