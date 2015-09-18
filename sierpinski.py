from visual import *
import random
import math

s = .003

def gasket():
    #scene.autoscale = False
    scene.center = vector(0, 0, 0)
    t = vector(0, 0, -10)
    for i in range(3000):
        r = random.randint(0, 2)
        if r == 0:
            t[0] *= .5
            t[1] *= .5
        elif r == 1:
            t[0] *= .5
            t[0] += .5
            t[1] *= .5
        elif r == 2:
            t[0] *= .5
            t[0] += .25
            t[1] *= .5
            t[1] += math.sqrt(3)/4.
            #t[1] += math.sqrt(11)/4.
        elif r == 3:
            x = t[0]
            t[0] = t[1]
            t[1] = x
        p = list(t)
        p[0] -= .5
        p[1] -= .5
        p[2] = 0
        sphere(radius=s, pos=p)
        

t = (
    (0,0,0),
    (0,0,1),
    (0,0,2),
    (0,1,0),
#    (0,1,1),
    (0,1,2),
    (0,2,0),
    (0,2,1),
    (0,2,2),
    (1,0,0),
#    (1,0,1),
    (1,0,2),
#    (1,1,0),
#    (1,1,1),
#    (1,1,2),
    (1,2,0),
#    (1,2,1),
    (1,2,2),
    (2,0,0),
    (2,0,1),
    (2,0,2),
    (2,1,0),
#    (2,1,1),
    (2,1,2),
    (2,2,0),
    (2,2,1),
    (2,2,2)
)
def sponge():
    #scene.autoscale = False
    #scene.center = vector(0, 0, -25)
    p = vector(0, 0, 0)
    for i in range(3000):
        r = random.randint(0, 19)
        x = t[r]
        p *= 1./3.
        for j in range(3):
            p[j] += x[j]/3.
        q = vector(p[0]-.5, p[1]-.5, p[2]-.5)
        sphere(radius=.01, pos=q)
  
gasket() 
