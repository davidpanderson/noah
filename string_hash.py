import hashlib

def string_hash(s, n):
    m = hashlib.md5()
    m.update(s.encode('utf-8'))
    x = m.hexdigest()
    y = int(x, 16)
    return y%n
