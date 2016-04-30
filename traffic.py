#each car will be a dictionary with the 'acc' or 'acc'eleration, 'pos', street, 'speed',
#and the route that it will take.
from visual import *

def model(car, light):
    x = 0
    ball = sphere(pos=(1, 2, 1), radius=0.5)
    tlight = sphere(pos=(10, 2, 1), radius=0.5, color=(1,0,0))
    for time in range(25):
        #if car['pos'] in car[route]:
            #car['pos'] = turn(car)
            #car[route].remove(car['pos'])
        dis = (car['speed'] / 4) * car['speed'] * 1/2
        if (car['pos'] + dis >= light):
            car['acc'] = -4
        car['speed'] += car['acc']
        if car['speed'] < 0:
            car['speed'] = 0
        car['pos'] += car['speed']
        if car['pos'] == light:
            break
        print(car)
        print(time)
        x = car['pos']
        x = x / 100
        ball.pos = [x, 2, 1]
        sleep(.1)

car = {'speed':60, 'acc':0, 'pos':0}
model(car, 1000)



        
            
