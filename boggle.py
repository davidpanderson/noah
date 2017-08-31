import math
from dict import *

# get_board() will ask the user what board to use.
def get_board(le):
    board = []
    for i in range(le^2 - 1):
        s = input(i)
        board.append(s)
    return board

# returns True if the num1 and num2 positions in the grid are next to echother,
# and False if they're not.
def check_two_num(num1, num2, len_row):
    num1_row = int(num1/len_row)
    num1_col = int(num1 % len_row)
    num2_row = int(num2/len_row)
    num2_col = int(num2 % len_row)
    if abs(num1_row - num2_row) < 2:
        if abs(num1_col - num2_col) < 2:
            return True
    return False
# checks if a word is in a boggle board. You should make positions_used be an empty ist, since it
# only used in the recursive function part.
def find_word(board, word, positions_used):
    len_row = int(math.sqrt(len(board)))
    if len(word) == len(positions_used):
        return True
    counter = 0
    if len(positions_used) > 1:
        letter = word[len(positions_used)-1]
    else:
        letter = word[0]
    for l in board:
        if l == letter:
            if len(positions_used) > 1:
                if check_two_num(counter, positions_used[len(positions_used)-1], len_row):
                    positions_used.append(counter)
                    return find_word(word, positions_used, l)
            else:
                positions_used.append(counter)
                return find_word(board, word, positions_used)
            if len(positions_used) > 1:
                del positions_used[len(positions_used)-1]
                return find_word(board, word, positions_used)
            counter += 1
    return False
# solve(board) wil solve the board that you enter. The board can be any size, as long as it's a
# square.
def solve(board):
    for w in get_dictionary(True, True):
        print (w )
        if find_word(b, w, []) == True:
            print(w)
b = ['a', 'n', 'e', 'r',
     's', 'e', 'h', 't',
     'm', 'o', 'l', 'i',
     'w', 'b', 'c', 'v']
print(find_word(b, 'ane', []))
