from visual import *
import random
import time

v = vector(0, 0, .1)
ready = False
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
    global ready
    print('key up')
    ready = True
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

def setup_window():
    scene.autoscale = False
    scene.center = vector(0, 0, -20)
    scene.bind('keydown', key_down)
    scene.bind('keyup', key_up)
    scene.bind('mousemove', mouse_move)
    d = display.get_selected()

def show_instructions():
    global ready
    instructions = text(text='', color=color.white, height=.4, pos=(-2, 3.5, -20))
    instructions.text = 'Welcome to Space Slalom!\nUse the mouse to steer through rings\nPress any key to start'
    ready = False
    while not ready:
        sleep(.1)
    instructions.visible = False
    del instructions

def play_game():
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
        p = vector(random.uniform(-s,s), random.uniform(-s,s), random.uniform(-60,-10))
        r = ring(pos=p, axis=a, color=random_color())
        rings.append(r)
    start = time.time()
    now = 0
    game_length = 180
    while True:
        sleep(.02)
        n = int(time.time()-start)
        if n > now:
            now = n
            rem = game_length - now
            if rem <= 0:
                break
            clock.text = str(rem)
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
    clock.visible = False
    hits.visible = False
    misses.visible = False
    del clock
    del hits
    del misses
    for r in rings:
        r.visible = False
        del r
    return nhits

def show_score(score):
    global ready
    instructions = text(text='', color=color.white, height=.4, pos=(-2, 3.5, -20))
    instructions.text = 'Congratulations! Your score is %d\nPress any key to play again' %(score)
    ready = False
    while not ready:
        sleep(.1)
    instructions.visible = False
    del instructions


def high_score_file(score):
    
    
def main():
    setup_window()
    show_instructions()
    while True:
        score = play_game()
        show_score(score)
        high_score_file(score)
main()
