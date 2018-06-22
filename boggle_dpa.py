import math, sys
import dict            # module for getting word list (regular or jumbo)

# program to find all the words in a Boggle board of arbitrary (square) size

# return True if the num1 and num2 positions in the grid are adjacent
# "edge" is the edge length of the grid
#
def adjacent(num1, num2, edge):
    num1_row = num1//edge
    num1_col = num1 % edge
    num2_row = num2//edge
    num2_col = num2 % edge
    if abs(num1_row - num2_row) >= 2:
        return False
    if abs(num1_col - num2_col) >= 2:
        return False
    return True

# recursive function, returns True if word is in board
# "used" is a list of board positions used so far
#
def find_word(board, word, used, n, edge):
    nused = len(used)
    if nused:
        last = used[nused-1]
    for i in range(n):
        if nused and i == last:
            continue
        if nused and not adjacent(i, last, edge):
            continue
        if board[i] != word[0]:
            continue
        if nused and i in used:
            continue
        used.append(i)
        if len(word) == 1:
            return True
        return find_word(board, word[1:], used, n, edge)
    return False

# print list of all words in board
#
def solve(board, min_length, jumbo):
    print(board)
    n = len(board)
    edge = int(math.sqrt(n))
    count = 0
    for w in dict.get_dictionary(jumbo, True):
        if len(w) < min_length:
            continue
        if find_word(board, w, [], n, edge):
            print(w)
            count += 1
    print 'count: ', count

def test():
    solve ([
     'a', 'n', 'e', 'r',
     's', 'e', 'h', 't',
     'm', 'o', 'l', 'i',
     'w', 'b', 'c', 'v'
      ], 4, False)

if (True):
    board = list(sys.argv[1])
    min_length = int(sys.argv[2])
    solve(board, min_length, len(sys.argv)>3)
else:
    test()
