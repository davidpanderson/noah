from collections import Counter
import dict

eng_letters = 'etaonrishdlfcmugypwbvkjxqz'

# return True if word matches pattern
#
def word_matches_pattern(wo, x):
    if len(x) != len(wo):
        return False
    for l in range(len(x)):
        t = x[l]
        if t != ' ':
            if wo[l] != x[l]:
                return False
    print 'match: ', wo
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

# return true if a guess is OK
# alpha: the alphabet, sorted by frequency
# crypt_chars: the letters in the cryptogram, sorted by frequency
# guess: a list of numbers;
#    guess[i] = n means that crypt_chars[i] is mapped to alpha[n]
# crypt_words: the list of words in the cryptogram
# "OK" means that there are actual words compatible with the guess
#
def guess_ok(alpha, crypt_chars, guess, crypt_words):
    x = []
    crypt = list(crypt)
    for c in crypt:
        for l in range(len(guess)):
            x.append

words = get_dictionary()

def solve_crypt(crypt):
    crypt_chars = creat_freq(crypt)
    crypt_words = crypt.split()
    guess = [0]
    print guess_ok(eng_letters, crypt_chars, guess, crypt_words)
