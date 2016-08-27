# read word-list file, return list of words (~109K of them)
#
def get_dictionary(big=False, alpha_only=True):
    if big:
        f = open("C:/Users/David/My Documents/words2.txt", 'r')
    else:
        f = open("C:/Users/David/My Documents/words.txt", 'r')
    x = []
    while True:
        word = f.readline()
        y = word
        word = word.strip()
        word = word.lower()
        if len(word) == 0:
            print(y)
            break
        if alpha_only and not word.isalpha():
            continue
        x.append(word)
    return x
    
# tell user whether strings are in dictionary.
# quit when get empty string
#
def check_words():
    dict = get_dictionary()
    while True:
        w = raw_input()
        w = w.strip()
        if len(w) == 0:
            break
        if w in dict:
            print(w, ' is a word')
        else:
            print (w, ' is not a word')

# return True if word is made of given letters and includes letters[0]
# (for the NY Times Spelling Bee game)
#
def word_matches(letters, word):
    w = list(word)
    for c in w:
        if c not in letters:
            return False
    return letters[0] in w
    
# given a string of letters, return the list of words made
# up of those letters and containing the first one.
# (for NY Times game)
#
def spelling_bee(letters):
    letter_list = list(letters)
    dict = get_dictionary()
    for w in dict:
        if len(w)<5:
            continue
        if word_matches(letter_list, w):
            print (w)

# return true if y has all the letters in x, in the same order
#
def license_match(x, y):
    x = list(x)
    y = list(y)
    r = []
    i = 0
    j = 0
    while True:
        if i >= len(x) or j >= len(y):
            break
        if x[i] == y[j]:
            r.append(x[i])
            i = i + 1
            j = j + 1
        else:
            j = j + 1
    return x == r

# Daddy's version of license_match()
#
def lm(x, y):
    x = list(x)
    y = list(y)
    i = 0
    j = 0
    while i<len(x) and j<len(y):
        if x[i] == y[j]:
            i += 1
        j += 1
    return i == len(x)

# return list of words that have w in them in the right order.
#
def lis_game(w):
    q = []
    d = get_dictionary()
    for i in d:
        if license_match(w, i):
            q.append(i)
    return q

# return list of all 3-letter sequences
#
def seq3():
    a = list('abcdefghijklmnopqrstuvwxyz')
    s = []
    for i in a:
        for j in a:
            for k in a:
                s.append(i+j+k)
    return s

# print sequences that match 3 words or less
#
def find3():
    seqs = seq3()
    d = get_dictionary()
    for s in seqs:
        m = []
        for i in d:
            if license_match(s, i):
                m.append(i)
            if len(m) > 3:
                break
        if len(m) <= 3:
            print (s, m)

# what does this do??
#
def wps(x):
    dict = get_dictionary()
    l = list('abcdefghijklmnopqrstuvwxyz') 
    x = list(x)
    for t in range(len(x)):
        i = x[t]
        for le in l:
            if i == ' ':
                x[t] = le
    if x in dict:
        return True
    else:
        return False

# print list of words that contain given substring
#
def extends(s):
    dict = get_dictionary()
    for w in dict:
        if  w.find(s) >= 0:
            print(w)
