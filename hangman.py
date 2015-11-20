import dict
import random

def hangman_graphic(guesses):
		if guesses == 0:
			print "________      "
			print "|      |      "
			print "|             "
			print "|             "
			print "|             "
			print "|             "
		elif guesses == 1:
			print "________      "
			print "|      |      "
			print "|      0      "
			print "|             "
			print "|             "
			print "|             "
		elif guesses == 2:
			print "________      "
			print "|      |      "
			print "|      0      "
			print "|     /       "
			print "|             "
			print "|             "
		elif guesses == 3:
			print "________      "
			print "|      |      "
			print "|      0      "
			print "|     /|      "
			print "|             "
			print "|             "
		elif guesses == 4:
			print "________      "
			print "|      |      "
			print "|      0      "
			print "|     /|\     "
			print "|             "
			print "|             "
		elif guesses == 5:
			print "________      "
			print "|      |      "
			print "|      0      "
			print "|     /|\     "
			print "|     /       "
			print "|             "
		else:
			print "________      "
			print "|      |      "
			print "|      0      "
			print "|     /|\     "
			print "|     / \     "
			print "|             "

def hangman():
    guesses = []
    d = dict.get_dictionary()
    w = random.choice(d)
    nleft = 6
    for i in w:
        print "_",
    print
    while True:
        hangman_graphic(6-nleft)
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
        

def play_hangman():
    while True:
        hangman()
        g = raw_input("play again? y/s")
        if g == "y":
            hangman()
        else:
            break
play_hangman()
        
        
                  
        
            

    
    
