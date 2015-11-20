

from visual import *
import random
import time

v = vector(0, 0, .1)

speed = .05
def key_down(evt):
    if evt.key == 'left':
        v[0] = speed
    elif evt.key == 'right':
        v[0] = -speed
    elif evt.key == 'up':
        v[1] = -speed
    elif evt.key == 'down':
        v[1] = speed

def key_up(evt):
    if evt.key == 'left':
        v[0] = 0
    elif evt.key == 'right':
        v[0] = 0
    elif evt.key == 'up':
        v[1] = 0
    elif evt.key == 'down':
        v[1] = 0

def mouse_move(evt):
    v[0] = -evt.pos[0]/100
    v[1] = -evt.pos[1]/100
    
def hit_ring(r):
    d = r.pos[0]*r.pos[0] + r.pos[1]*r.pos[1]
    return d<1

def random_color():
    return (random.uniform(.5, 1), random.uniform(.5, 1), random.uniform(.5, 1))
def play_game():
    scene.autoscale = False
    scene.center = vector(0, 0, -20)
    scene.bind('keydown', key_down)
    scene.bind('keyup', key_up)
    scene.bind('mousemove', mouse_move)
    d = display.get_selected()

    s = 3    # determines x/y spacing of rings

    clock = text(text='0', color=color.green, pos=(-10, 5, -20))
    hits = text(text='hits:', color=color.green, pos=(6, 5, -20))
    misses = text(text='misses:', color=color.green, pos=(6, 3.5, -20))
    
    rings = []
    n = 10
    a = vector(0, 0, 1)
    nhits = 0
    nmisses = 0
    for i in range(n):
        p = vector(random.uniform(-s,s), random.uniform(-s,s), random.uniform(-50,0))
        r = ring(pos=p, axis=a, color=random_color())
        rings.append(r)
    start = time.time()
    now = 0
    while True:
        sleep(.02)
        n = int(time.time()-start)
        if n > now:
            now = n
            clock.text = str(n)
        #d.background = (0, 0, 0)
        for r in rings:
            r.pos += v
            if r.pos[2] > 0:
                if hit_ring(r):
                    #d.background = (0, 1, 0)
                    nhits += 1
                    hits.text = 'hits: '+str(nhits)
                else:
                    nmisses += 1
                    misses.text = 'misses: '+str(nmisses)
                    #d.background = (1, 0, 0)
                r.pos = (random.uniform(-s,s), random.uniform(-s,s), random.uniform(-55, -50))

play_game()
