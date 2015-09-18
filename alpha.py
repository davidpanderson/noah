import random
from dict import *

def show_guesses(guesses, words, n):
    i = guesses[-1]
    w = words[i]
    if i < n:
        print 'my word is after %s' %(w)
    else:
        print 'my word is before %s' %(w)

    lower = -1
    upper = 999999
    for g in guesses:
        if g < n:
            if g > lower:
                lower = g
        else:
            if g < upper:
                upper = g
    i = 1
    for g in guesses:
        x = ''
        if g == lower:
            x = ' (after)'
        elif g == upper:
            x = ' (before)'
        print '%d. %s%s' %(i, words[g], x)
        i += 1

def play_game(words):
    n = random.randint(0, len(words)-1)
    guesses = []
    while True:
        w = raw_input('Guess: ')
        w = w.strip()
        if not w:
            print 'the word is %s' %(words[n])
            break
        if w not in words:
            print '%s is not a word' %(w)
            continue
        i = words.index(w)
        if i == n:
            print 'Woo hoo!  you guessed the word'
            break
        guesses.append(i)
        show_guesses(guesses, words, n)

words = get_dictionary()
while True:
    play_game(words)
    x = raw_input('Play again? (y/n): ')
    if x != 'y':
        break
