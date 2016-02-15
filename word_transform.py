from dict import *

# return word with last 2 chars switched
#
def transform(w):
    n = len(w)
    w2 = w[:-2]
    w2 += w[n-1]
    w2 += w[n-2]
    return w2

def reverse(w):
    return w[::-1]

# print words whose transform is also a word
#
def word_transform():
    words = get_dictionary()
    d = {}
    for word in words:
        d[word] = True
        
    for word in words:
        if len(word) < 2:
            continue
        #w2 = transform(word)
        w2 = reverse(word)
        if word <= w2:
            continue
        if w2 in d.keys():
            print(word, w2)

word_transform()
