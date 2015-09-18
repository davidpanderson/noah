import random

# return 0 if tie, 1 if i wins, 2 if j wins
#
def decide(i, j):
    return (i-j)%3
    
b = [0, 0, 0]
def game():
    j = ["rock", "paper", "scissors"]
    outcomes = ["tie", "you lost", "you win"]
    while True:
        choice = random.randint(0, 2)
        g = raw_input("what are you going to play in rock paper scissors? ")
        if g not in j:
            break
        print "I picked ", j[choice]
        d = decide(choice, j.index(g))
        print outcomes[d]
        b[d] = b[d] + 1
        print b[2], 'wins', b[1], 'loses', b[0], 'ties'
        
game()       
