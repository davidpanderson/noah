import dict
import random
def hangman():
    guesses = []
    d = dict.get_dictionary()
    w = random.choice(d)
    nleft = 6
    for i in w:
        print "_",
    print
    while True:
        guess = raw_input("what is your guess? ")
        if guess in guesses:
            print "you already guessed that"
            continue
        guesses.append(guess)
        nmatch = 0
        for c in w:
            if c in guesses:
                print c,
                nmatch += 1
            else:
                print "_",
        print
        if guess not in w:
            print "incorrect"
            nleft -= 1
            print "you have",
            print nleft,
            print "wrong guesses left"
        if nmatch == len(w):
            print "you win!"
            break
        if nleft == 0:
            print "you lose!"
            print w
            break

hangman()
        
            

    
    
