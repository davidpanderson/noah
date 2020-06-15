def return_factors(n):
    factors = []
    for i in range(n+1):
        if n%i == 0:
            factors += i
    return factors

f = return_factors(600851475143)
highest_prime = 0
for i in f:
    if len(return_factors(i)) == 2:
        highest_prime = i
    if i > 6008514751432:
        break
print(highest_prime)
