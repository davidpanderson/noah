from visual import *
for i in range(100):
    f = ring(pos=(1,-1,3), axis=(1,-1,3), radius=1, thickness=.345)
    f.pos[1] = f.pos[1] + 1
ring()

