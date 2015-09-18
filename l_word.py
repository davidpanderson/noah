import dict
x = 0
for i in dict.get_dictionary():
	if len(i) > x:
		x = len(i)
		print i
print x
