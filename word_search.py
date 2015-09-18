import dict
import random

words = dict.get_dictionary()

w = random.choice(words)

while True:
    g = raw_input('Guess: ')
    if  g not in words:
        print g+' is not a word'
        continue
