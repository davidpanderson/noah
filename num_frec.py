#import numpy as np
import random

def test_frec(digits, num):
    cou = 0
    number = []
    for i in range(len(num)):
        #number.append(np.random.random_integers(9))
        number.append(random.randint(0,9))
    for d in range(digits):
        #number.append(np.random.random_integers(9))
        number.append(random.randint(0,9))
        del number[0]
        if number == num:
            cou += 1
        if d % 100000 == 1:
            print(d, float(cou)/d)

test_frec(30000000, [3,3,3,3])
