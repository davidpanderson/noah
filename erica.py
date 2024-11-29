# in the following, a "letter set" is represented
# by a string in which the characters are alphabetized

import dict,sys

words = dict.get_dictionary()

# for each length, make a dict that maps letters set
# to the list of words with those letters
#
def div_by_len():
    words_by_len = [None]*40
    for i in range(40):
        words_by_len[i] = {}
    for w in words:
        w2 = ''.join(sorted(w))
        wl = len(w)
        wbl = words_by_len[wl]
        if w2 in wbl:
            wbl[w2].append(w)
        else:
            wbl[w2] = [w]
    return words_by_len

# See if there is a word triangle starting with the given letter set.
# If there is, print the words for the letter set, and return True
#
def triangle(w, wbl, show):
    if len(w) == 1:
        if w in wbl[1]:
            if show: print(w)
            return True
        else:
            return False

    # remove one letter at a time.
    # keep track of ones already removed
    #
    wlist = list(w)
    found = False
    tried = []
    for i in range(len(w)):
        w2 = list(wlist)
        if w2[i] in tried:
            continue
        tried.append(w2[i])
        del(w2[i])
        w2 = ''.join(w2)
        #print('trying ', w2)
        if w2 in wbl[len(w2)]:
            if triangle(w2, wbl, show):
                if show:
                    words = wbl[len(w2)][w2]
                    print(' '.join(words))
                found = True
            else:
                #print("can't complete triangle")
                continue
        else:
            #print('no words with those letters')
            continue
    return found

# find the longest word that has a triangle
#
def main():
    wbl = div_by_len()
    if True:
        x = ''.join(sorted('rational'))
        triangle(x, wbl, True)
        return

    words2 = []
    for w in words:
        words2.append(w)
    words2.sort(key=lambda x: -len(x))
    for w in words2:
        x = ''.join(sorted(w))
#print(w)
        if triangle(x, wbl, False):
            triangle(x, wbl, True)
            print('-------- solved %s'%w)
            sys.stdin.read(1)
        else:
            pass
#print('no solution')

main()
