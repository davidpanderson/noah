from visual import *
from random import *
scene.autoscale = False
scene.center = vector(0, 0, -20)
d = display.get_selected()
def random_color():
    return (random.uniform(.5, 1), random.uniform(.5, 1), random.uniform(.5, 1))
def create_random_object():
    rc = random_color()
    box(col=rc)

    
create_random_object()
