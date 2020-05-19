#!/usr/bin/python

import hashlib


def intTryParse(value):
    try:
	int(value)
        return True
    except ValueError:
        return False

hashed = ""
value = ""
i = 0
while intTryParse(hashed) == False:
	i = i + 1
	value = str(i) + "Pinkflood"
	hashed = hashlib.md5(value).hexdigest()
	print hashed
	print value
print 'WIN !!'
