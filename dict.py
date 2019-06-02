import sys

# read word-list file, return list of words (~109K of them)
#
def get_dictionary(big=False, alpha_only=True):
    if big:
        f = open("words2.txt", 'r')
    else:
        f = open("words.txt", 'r')
    x = {}
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
        x[word] = 1
    return x
    
# tell user whether strings are in dictionary.
# quit when get empty string
#
def check_words():
    dict = get_dictionary()
    while True:
        w = input()
        w = w.strip()
        if len(w) == 0:
            break
        if w in dict:
            print(w, ' is a word')
        else:
            print (w, ' is not a word')

#check_words()

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

# print list of words whose letters are in alphabetic order
#
def alpha_order():
    dict = get_dictionary()
    for w in dict:
        z = list(w)
        flag = True
        for i in range(len(z)-1):
            if z[i] >= z[i+1]:
                flag = False
                break
        if flag and len(w)>5:
            print(w)

#alpha_order()

def reverse_words():
    dict = get_dictionary()
    for w in dict:
        if w[::-1] in dict and len(w)>5:
            print(w)

#reverse_words()

def shift_word(w, k):
    n = len(w)
    return w[k:n]+w[0:k]

def shift_words():
    dict = get_dictionary()
    for w in dict:
        if shift_word(w, 1) in dict and len(w)>5:
            print(w)

#shift_words()

def swap_letters(w, a, b):
    x = list(w)
    founda = False
    foundb = False
    for i in range(len(x)):
        if x[i] == a:
            x[i] = b;
            founda = True
        elif x[i] == b:
            x[i] = a;
            foundb = True
    if founda and foundb:
        return ''.join(x)
    return ''

# words that have m and n, and swapping them is also a word
def swap():
    dict = get_dictionary()
    for w in dict:
        if swap_letters(w, 'm', 'n') in dict and len(w)>5:
            print(w)

# words that have all 5 vowels
def all_vowels():
    dict = get_dictionary()
    for w in dict:
        if len(w)>9:
            continue
        y = list(w)
        if not 'a' in y:
            continue
        if not 'e' in y:
            continue
        if not 'i' in y:
            continue
        if not 'o' in y:
            continue
        if not 'u' in y:
            continue
        print(w)

# words made of 2 sub-words
#
def word_pairs():
    dict = get_dictionary()
    for w in dict:
        n = len(w)
        for i in range(3, n-3):
            a = w[0:i]
            if not a in dict:
                continue
            b = w[i:n]
            if not b in dict:
                continue
            print(w, a, b)

def word_triples():
    m = 4
    dict = get_dictionary(False)
    for w in dict:
        n = len(w)
        if n < m*3:
            continue
        for i in range(m, n-2*m):
            a = w[0:i]
            if not a in dict:
                continue
            for j in range(i+m, n-m):
                b = w[i:j]
                c = w[j:n]
                if not b in dict or not c in dict:
                    continue
                print(w, a, b, c)
            
# words made up of pairs of adjacent letters
#
def letter_pairs():
    dict = get_dictionary()
    for w in dict:
        n = len(w)
        if n%2:
            continue
        x = list(w)
        found = False
        for i in range(n // 2):
            a = chr(ord(x[i*2])+1);
            #print(x[0], ord(x[0]), chr(ord(x[0])))
            b = x[i*2+1];
            #print(i, w, a, b)
            if a != b:
                found = True
                break
        if found:
            continue
        print(w)

# word pairs of the form *or *id
#
def orid():
    dict = get_dictionary(True)
    for w in dict:
        n = len(w)
        if w[n-2:n] != 'or':
            continue
        if w[0:n-2] + 'id' not in dict:
            continue
        print(w)

if sys.argv[1] == 'license_plate':
    x = lis_game(sys.argv[2])
    for w in x:
        print w
elif sys.argv[1] == 'spelling_bee':
    spelling_bee(sys.argv[2])
