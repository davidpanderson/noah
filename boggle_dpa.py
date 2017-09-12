import math
from dict import *



# returns True if the num1 and num2 positions in the grid are adjacent
def adjacent(num1, num2, len):
    num1_row = num1//len
    num1_col = num1 % len
    num2_row = num2//len
    num2_col = num2 % len
    if abs(num1_row - num2_row) >= 2:
        return False
    if abs(num1_col - num2_col) >= 2:
        return False
    return True

def find_word(board, word, used, n, edge):
    nused = len(used)
    if nused:
        last = used[nused-1]
    for i in range(n):
        if nused and i == last:
            continue;
        if nused and not adjacent(i, last, edge):
            continue;
        if board[i] != word[0]:
            continue
        if nused and i in used:
            continue
        used.append(i)
        if len(word) == 1:
            #print(used)
            return True
        return find_word(board, word[1:], used, n, edge)
    return False
    
 
def solve(board):
    n = len(board)
    edge = math.sqrt(n)
    count = 0
    for w in get_dictionary(False, True):
        if len(w) < 4:
            continue;
        if find_word(b, w, [], n, edge):
            print(w)
            count += 1
    print('count: ', count)
    
b = ['a', 'n', 'e', 'r',
     's', 'e', 'h', 't',
     'm', 'o', 'l', 'i',
     'w', 'b', 'c', 'v']

solve(b)
    
