class high_score():
    def __init__(num, l, n):
        num.n = n
        num.l = l
    def score(num, x):
        
        if len(num.n) < num.l:
            num.n.append(x)
        elif num.n[len(num.n) - 1] < x:
            num.n.append(x)
            num.n.sort()
            num.n.remove(num.n[len(m)])
        return num.n        
                
