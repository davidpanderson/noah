
from visual import *
import random
import time
import datetime
from operator import itemgetter

v = vector(0, 0, .1)
ready = False
speed = .05
vscale = 1.
quit = False;

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
    global ready, quit
    ready = True
    if evt.key == 'left':
        v[0] = 0
    elif evt.key == 'right':
        v[0] = 0
    elif evt.key == 'up':
        v[1] = 0
    elif evt.key == 'down':
        v[1] = 0
    elif evt.key == 'esc':
        quit = True

def mouse_move(evt):
    global vscale
    v[0] = -evt.pos[0]/100
    v[1] = -vscale*evt.pos[1]/100
    
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

def show_instructions():
    global ready
    instructions = text(text='', color=color.white, height=.4, pos=(-2, 3.5, -20))
    instructions.text = 'Welcome to Space Slalom!\nUse the mouse to steer through rings.\nPress any key to start.'
    ready = False
    while not ready:
        sleep(.1)
    instructions.visible = False
    del instructions

# given the position of a ring, compute a position for the following ring.
# dz is uniformly distributed over (A, B)
# dx and dy are uniform over (-Cdz, Cdz)
# So A, B and C define the nature and difficulty of the game
#
def next_pos(pos):
    dz = random.uniform(0.5, 8.0)
    cdz = .8*dz
    dx = random.uniform(-cdz, cdz) - pos[0]/2
    dy = random.uniform(-cdz, cdz) - pos[1]/2
    p2 = vector(pos[0]+dx, pos[1]+dy, pos[2]-dz)
    #print(pos, p2)
    return p2

def play_game(game_length):
    global vscale, quit
    d = display.get_selected()
    vscale = d.width/d.height
    s = 3    # determines x/y spacing of rings
    ht = .6
    c = color.white
    clock = text(text='0', color=c, pos=(-10, 5, -20), height=ht)
    hits = text(text='hits:', color=c, pos=(6, 5, -20), height=ht)
    misses = text(text='misses:', color=c, pos=(6, 4, -20), height=ht)
    projt = text(text='projected:', color=c, pos=(6, 3, -20), height=ht)
    rings = []
    nrings = 10
    a = vector(0, 0, 1)
    nhits = 0
    nmisses = 0
    for i in range(nrings):
        if i == 0:
            p = vector(0, 0, -10)
        else:
            p = next_pos(p)
        #p = vector(random.uniform(-s,s), random.uniform(-s,s), random.uniform(-60,-10))
        r = ring(pos=p, axis=a, color=random_color())
        rings.append(r)
    start = time.time()
    now = 0
    dt = .02
    nsteps = 0
    quit = False
    while True:
        if quit:
            break;
        sleep(dt)
        nsteps += 1
        n = int(nsteps*dt)
        if n > now:
            now = n
            rem = game_length - now
            if rem <= 0:
                break
            clock.text = str(rem)
            projt.text = 'projected:  %.1f'%(nhits / (nsteps*dt) * game_length)
        #d.background = (0, 0, 0)
        for i in range(nrings):
            r = rings[i]
            r.pos += v
            if r.pos[2] > 0:
                if hit_ring(r):
                    #d.background = (0, 1, 0)
                    nhits += 1
                    hits.text = 'hits:  '+str(nhits)
                else:
                    nmisses += 1
                    misses.text = 'misses:  '+str(nmisses)
                    #d.background = (1, 0, 0)
                #r.pos = (random.uniform(-s,s), random.uniform(-s,s), random.uniform(-55, -50))
                j = (i+nrings-1) % nrings
                r.pos = next_pos(rings[j].pos)
    clock.visible = False
    hits.visible = False
    misses.visible = False
    projt.visible = False
    del clock
    del hits
    del misses
    del projt
    for r in rings:
        r.visible = False
        del r
    return nhits

def get_score(x):
    return x[1]

# read high score file and return sorted list of lists
#
def read_scores():
    f = open("scores.txt", "r")
    scores = []
    for line in f:
        x = line.split('|')
        x[1] = int(x[1])
        x[2] = float(x[2])
        scores.append(x)
    return sorted(scores, key=itemgetter(1), reverse=True)

# return a string of top 10 scores
#
def top_ten(scores):
    n = 1
    x = ''
    for s in scores:
        t = time.gmtime(s[2])
        x += '%d) %d %s %s\n'%(n, s[1], s[0], time.strftime("%B %d %Y", t))
        if n == 10:
            break
        n += 1
    return x
    
def show_score(score, t):
    global ready
    scores = read_scores()
    i = 1
    for s in scores:
        if s[2] == t:
            break
        i += 1
    
    instructions = text(text='', color=color.white, height=.4, pos=(-6, 3.5, -20))
    instructions.text = 'Your score is %d (#%d out of %d)\n\n'%(score, i, len(scores))
    instructions.text += top_ten(scores)
    instructions.text += '\nPress any key to play again'
    ready = False
    while not ready:
        sleep(.1)
    instructions.visible = False
    del instructions

# append score to high score file
#
def write_score(name, score, t):
    f = open("scores.txt", "a")
    f.write("%s|%d|%s\n" %(name, score, t))
    f.close()

def main():
    print 'Enter your name: ',
    name = raw_input()
    setup_window()
    show_instructions()
    while True:
        t = round(time.time())
        score = play_game(100)
        write_score(name, score, t)
        show_score(score, t)
main()
