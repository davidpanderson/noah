from collections import Counter
import dict

eng_letters = 'etaonrishdlfcmugypwbvkjxqz'
crypt_chars = ''

# return True if word matches pattern
# (a "pattern" is a string where spaces are wild card)
#
def word_matches_pattern(wo, x):
    if len(x) != len(wo):
        return False
    for l in range(len(x)):
        t = x[l]
        if t != ' ':
            if wo[l] != x[l]:
                return False
    print ('match: ', wo)
    return True

# return True if any word matches pattern
#
def any_word_matches_pattern(x):
    for wo in words:
        if word_matches_pattern(wo, x):
            return True
    return False

# given a string s, return a list of unique alpha chars in s,
# ordered by decreasing frequency
def creat_freq(s):
    x = Counter(s)
    y = x.most_common()
    a = []
    for z in y:
        if z[0].isalpha():
            a.append(z[0])
    return a

# convert a guess into a letter-subtitution map
#
def guess_to_map(guess):
    x = {}
    for i in range(len(guess)):
        j = guess[i]
        print (i, j, crypt_chars[i])
        x[crypt_chars[i]] = eng_letters[j]
    return x
        
# given a cryptogram word and a guess, create the corresponding pattern
#
def make_pattern(w, map):
    p = ''
    for c in w:
        if c in map:
            p += map[c]
        else:
            p += ' '
    return p
        
        
# return true if a guess is OK
# alpha: the alphabet, sorted by decreasing frequency
# crypt_chars: the letters in the cryptogram, sorted by decreasing frequency
# guess: a list of numbers;
#    guess[i] = n means that crypt_chars[i] is mapped to alpha[n]
# crypt_words: the list of words in the cryptogram
# "OK" means that there are actual words compatible with the guess
#
def guess_ok(guess, crypt_words):
    map = guess_to_map(guess)
    for w in crypt_words:
        p = make_pattern(w, map)
        if not any_word_matches_pattern(p):
            return False
    return True

words = dict.get_dictionary()

def solve_crypt(crypt):
    global crypt_chars
    crypt_chars = creat_freq(crypt)
    print 'crypt chars: ',crypt_chars
    crypt_words = crypt.split()
    guess = [0]
    print guess_ok(guess, crypt_words)

print(solve_crypt('xym oliny'))
