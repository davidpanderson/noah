import pygame
import sys
import math
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PINK = (255, 192, 203)
PURPLE = (128, 0, 128)
GRAY = (128, 128, 128)
# initial positions of the fielders:

# Initializing Pygame
pygame.init()
running = True
# Changing surface color
b1_x = 480
b1_y = 640
b2_x = 480
b2_y = 380
ss_x = 420
ss_y = 320
b3_x = 140
b3_y = 320
lf_x = 650
lf_y = 600
cf_x = 600
cf_y = 300
rf_x = 200
rf_y = 50
p_x = 250
p_y = 550
c_x = 10
c_y = 790
ball_x = 250
ball_y = 550
ball_x_v = 0
ball_y_v = 0
ball_x_a = 0
ball_y_a = 0
surface = pygame.display.set_mode((800, 800))
surface.fill(RED)
def draw_fielders():
        #first baseman
        b1 = pygame.draw.circle(surface,
               GRAY, (b1_x, b1_y), (20), 0)
        b2 = pygame.draw.circle(surface,
               GRAY, (b2_x, b2_y), (20), 0)
        ss = pygame.draw.circle(surface,
               GRAY, (ss_x, ss_y), (20), 0)
        b3 = pygame.draw.circle(surface,
               GRAY, (b3_x, b3_y), (20), 0)
        lf = pygame.draw.circle(surface,
               GRAY, (lf_x, lf_y), (20), 0)
        cf = pygame.draw.circle(surface,
               GRAY, (cf_x, cf_y), (20), 0)
        rf = pygame.draw.circle(surface,
               GRAY, (rf_x, rf_y), (20), 0)
        p = pygame.draw.circle(surface,
               GRAY, (p_x, p_y), (20), 0)
        c = pygame.draw.circle(surface,
               GRAY, (c_x, c_y), (20), 0)

def move_ball():
    global ball_x, ball_y, ball_x_v, ball_y_v, ball_y_a, ball_x_a
    if ball_x_a <= 0:
        return
    ball_x += ball_x_v
    ball_y += ball_y_v
    ball_x_a -=1
    ball_y_a-=1
    
def fill_screen(runner_x, runner_y):
    surface.fill(RED)
    pygame.draw.rect(surface, (0, 0, 255),
                     [80, 320, 400, 400], 2)
    pygame.draw.line(surface, WHITE,
                    (80, 720), (80, 0), 4)
    pygame.draw.line(surface, WHITE,
                    (80, 720), (800, 720), 4)
    runner = pygame.draw.circle(surface,
               GRAY, (runner_x,runner_y), (20), 0)
    draw_fielders()
    ball = pygame.draw.circle(surface,
               GRAY, (ball_x, ball_y), (20), 0)
    pygame.display.flip()
    pygame.display.update()
def home_to_first(time):
    for i in range(100):
        move_ball()
        fill_screen(80+4*i, 720)
        pygame.time.wait(time)
def first_to_second(time):
    move_ball()

    for i in range(100):
        fill_screen(480, 720-4*i)
        pygame.time.wait(time)
def second_to_third(time):
    move_ball()
    for i in range(100):
        fill_screen(480-4*i, 320)
        pygame.time.wait(time)
def third_to_home(time):
    move_ball()
    for i in range(100):
        fill_screen(80, 320+4*i)
        pygame.time.wait(time)
        
def hit():
    global ball_x, ball_y, ball_x_v, ball_y_v, ball_x_a, ball_y_a
    if ball_x>40 and ball_x<120 and ball_y>660 and ball_y<780:
        ball_x_v = 3
        ball_y_v = -5
        ball_x_a = 100
        ball_y_a = 100
        home_to_first(10)
        first_to_second(10)
        ball_x_v = 0
        ball_y_v = 0
def find_closest_fielder():
    global ball_x, ball_y, ball_x_v, ball_y_v, ball_x_a, ball_y_a, b1_x, b1_y
    global b2_x, b2_y, ss_x, ss_y, b3_x, b3_y, p_x, p_y, lf_x, lf_y, cf_x
    global cf_y, rf_x, rf_y, c_x, c_y
    b = [ball_x, ball_y]
    db1 = math.dist(b, [b1_x, b1_y])    
def pitch(speed):
    global ball_x, ball_y
    ball_x = 250
    ball_y = 550
    ball = pygame.draw.circle(surface,
               GRAY, (ball_x, ball_y), (20), 0)
    swing = False
    for i in range(100):
        ev = pygame.event.get()
        for event in ev:
            if event.type == pygame.KEYDOWN:
                swing = True
        if swing:
            hit()
            break
        ball_x -= 2.5
        ball_y += 2.5
        fill_screen(80, 720)
        pygame.time.wait(speed)
    return False
        
fill_screen(80, 720)
#time in milliseconds
for i in range(10):
    pitch(20)
    pygame.time.wait(5000)


    
speed = 30
while running:
    
     for event in pygame.event.get():
           # checking if keydown event happened or not
        if event.type == pygame.KEYDOWN:
               
            # checking if key "A" was pressed
            if event.key == pygame.K_1:
                #fill_screen(480, 720)
                home_to_first(speed)
                draw_fielders()
            if event.key == pygame.K_2:
              #  fill_screen(480, 320)
              home_to_first(speed)
              first_to_second(speed)
            if event.key == pygame.K_3:
                home_to_first(speed)
                first_to_second(speed)
                second_to_third(speed)
            #    fill_screen(80, 320)
            if event.key == pygame.K_0 or event.key == pygame.K_4:
            #    fill_screen(80, 720)
                home_to_first(speed)
                first_to_second(speed)
                second_to_third(speed)
                third_to_home(speed)
            pygame.display.update()

        # if event is of type quit then 
        # set running bool to false
        #if event.type == pygame.QUIT:
         #   running = False
