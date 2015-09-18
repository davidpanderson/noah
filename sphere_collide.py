import random
import winsound
from visual import *

def rand_vector(x, y):
    return vector(random.uniform(x, y), random.uniform(x, y), random.uniform(x, y))

def collide(s1, s2):
    d = s1.pos - s2.pos
    return mag(d) <= s1.radius + s2.radius

def collide_list(s, slist):
    for s2 in slist:
        if collide(s, s2):
            return True
    return False

# move spheres, and bounce off walls
#
def bounce_walls(slist):
    for s in slist:  
        s.pos = s.pos + s.vel
        for i in range(3):
            if s.pos[i] < -1:
                if s.vel[i]<0:
                    s.vel[i] *= -1
                s.pos[i] = -1
            elif s.pos[i] > 1:
                if s.vel[i] > 0:
                    s.vel[i] *= -1
                s.pos[i] = 1

# make 2 spheres bounce off each other
#
def bounce(s1, s2):
    #winsound.PlaySound("C:\Users\David\Desktop\click_x.wav", winsound.SND_FILENAME | winsound.SND_ASYNC )
    d = s2.pos - s1.pos
    normal = norm(d)
    x = dot(s1.vel, normal)
    s1.vel = s1.vel - (2.*x)*normal
    x = dot(s2.vel, normal)
    s2.vel = s2.vel - (2.*x)*normal

    # the spheres overlap; separate them
    x = s1.radius + s2.radius - mag(d)
    s1.pos -= normal*x/2.
    s2.pos += normal*x/2
    
def bounce_spheres(slist):
    n = len(slist)
    for i in range(n):
        s1 = slist[i]
        for j in range(i+1, n):
            s2 = slist[j]
            if collide(s1, s2):
                bounce(s1, s2)
                
def rand_spheres(n):
    r = .14
    L=1+r
    gray = (0.7,0.7,0.7)
    xaxis = curve(pos=[(-L,-L,-L), (L,-L,-L)], color=gray)
    yaxis = curve(pos=[(-L,-L,-L), (-L,L,-L)], color=gray)
    zaxis = curve(pos=[(-L,-L,-L), (-L,-L,L)], color=gray)
    xaxis2 = curve(pos=[(L,L,L), (-L,L,L), (-L,-L,L), (L,-L,L)], color=gray)
    yaxis2 = curve(pos=[(L,L,L), (L,-L,L), (L,-L,-L), (L,L,-L)], color=gray)
    zaxis2 = curve(pos=[(L,L,L), (L,L,-L), (-L,L,-L), (-L,L,L)], color=gray)

    steps = 10000
    s = []
    for i in range(n):
        p = rand_vector(-1, 1.)
        if i%3 == 0:
            #c = rand_vector(.3, 1.)
            #s2 = sphere(radius=.1, pos=p, color=c)
            s2 = sphere(radius=r, pos=p, material=materials.BlueMarble)
        elif i%3 == 1:
            s2 = sphere(radius=r, pos=p, material=materials.marble)
        else:
            #s2 = sphere(radius=r, pos=p, material=materials.bricks)
            m = materials.loadTGA("C:\Users\David\Desktop\IMAG0101")
            t = materials.texture(data=m)
            s2 = sphere(radius=r, pos=p, material=t, axis=(0,0,1))
        while collide_list(s2, s):
            s2.pos = rand_vector(-1, 1)
        s.append(s2)
        s2.vel = rand_vector(-.02, .02)
    for i in range(steps):
        sleep(.01)
        #rate(100)
        bounce_walls(s)
        bounce_spheres(s)
        
rand_spheres(50)
