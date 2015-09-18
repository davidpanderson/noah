from visual import *
import random

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

c = [.7, .7, .7]

def change_color():
    for i in range(3):
        c[i] += random.uniform(-.1, .1)
        if c[i]>1:
            c[i] = 1
        elif c[i] < .4:
            c[i] = .4

def sponge(pos, size, depth):
    if depth == 0:
        box(pos=pos, length=size, height=size, width=size, color=c)
        change_color()
        return
    for a in t:
        pos2 = list(pos)
        for i in range(3):
            pos2[i] += a[i]*size/3.
        sponge(pos2, size/3., depth-1)
            

sponge([0., 0., 0.], 1., 3)
