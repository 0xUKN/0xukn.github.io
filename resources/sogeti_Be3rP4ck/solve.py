#!/usr/bin/python

import string

def sogehash(REF):
	prev = 0x00
	out = ""
	for char in REF:
		new_char = ((ord(char) << 2) ^ ord(char))
		out += "%x" % ((((ord(char) << 2) ^ ord(char)) ^ (prev >> 8)) & 0xff)
		prev = new_char
	return out

def un_sogehash(REF, current = ""):
	if len(current) == len(REF):
		return current
	elif len(current) == 0:
		prev = 0x00
	else:
		prev = ((ord(current[-1]) << 2) ^ ord(current[-1]))	
	for char in string.printable:
		new_char = ((((ord(char) << 2) ^ ord(char)) ^ (prev >> 8)) & 0xff)
		if new_char == ord(REF[len(current)]):
			new = un_sogehash(REF, current+char)
			if new == False:
				pass
			else:
				return new
	return False
	
print "UNHASH : " + str(un_sogehash("1f4e509605c9f4bf22f4bf22a5c9fe23bbfee5dd22ffdde5fb22aafedcdd22f5f1d6f0a4a5a589".decode('hex')))
