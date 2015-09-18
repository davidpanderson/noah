# program to play the "24" game

import itertools

def do_op(n1, n2, op):
    if op == '+':
        return n1 + n2
    if op == '-':
        x = n1 - n2
        if x < 0:
            raise ZeroDivisionError
        return x
    if op == '*':
        return n1 * n2
    if op == '/':
        if n1 % n2:
            raise ZeroDivisionError
        return n1 / n2

# the set of parenthesizations is:
# a(b(cd))    210
# (ab)(cd)   021 = 201
# ((ab)c)d    012
# (a(bc))d   102
# a((bc)d)   120

def parens(nums, ops, target):
    ans = []
    # try a(b(cd))
    try:
        x = do_op(nums[2], nums[3], ops[2])
        y = do_op(nums[1], x, ops[1])
        z = do_op(nums[0], y, ops[0])
        if z == target:
            ans.append("%d%s(%d%s(%d%s%d)) = %d"% (nums[0], ops[0], nums[1], ops[1], nums[2], ops[2], nums[3], target))
    except ZeroDivisionError:
        pass

    try:
        a = do_op(nums[0], nums[1], ops[0])
        b = do_op(a, do_op(nums[2], nums[3], ops[2]), ops[1])
        if b == target:
            ans.append("(%d%s%d)%s(%d%s%d) = %d"% (nums[0], ops[0], nums[1], ops[1], nums[2], ops[2], nums[3], target))
    except ZeroDivisionError:
        pass       
    try:
        a = do_op(nums[0], nums[1], ops[0])
        b = do_op(a, nums[2], ops[1])
        c = do_op(b, nums[3], ops[2])
        if c == target:
            ans.append("((%d%s%d)%s%d)%s%d = %d"% (nums[0], ops[0], nums[1], ops[1], nums[2], ops[2], nums[3], target))
    except ZeroDivisionError:
        pass

    try:   #(a(bc))d
        x = do_op(nums[1], nums[2], ops[1])
        y = do_op(nums[0], x, ops[0])
        z = do_op(y, nums[3], ops[2])
        if z == target:
            ans.append("(%d%s(%d%s%d))%s%d = %d"% (nums[0], ops[0], nums[1], ops[1], nums[2], ops[2], nums[3], target))
    except ZeroDivisionError:
        pass

    try:   #a((bc)d)
        x = do_op(nums[1], nums[2], ops[1])
        y = do_op(x , nums[3], ops[2])
        z = do_op(nums[0], y, ops[0])
        if z == target:
            ans.append("%d%s((%d%s%d)%s%d) = %d"% (nums[0], ops[0], nums[1], ops[1], nums[2], ops[2], nums[3], target))
    except ZeroDivisionError:
        pass
    return ans

def play(nums, target):
    ans = []
    ops = ['+', '-', '*', '/']
    for n in itertools.permutations(nums):
        for op in itertools.product(ops, repeat=3):
            ans = ans + parens(n, op, target)
    return ans

def print_list(x):
    for item in x:
        print item

s = raw_input()
numbers = map(int, s.split())


print_list(play(numbers, 24))

