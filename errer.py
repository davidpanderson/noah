class foo(Exception):
    pass
try:
    raise foo
except:
    print('noonel')
