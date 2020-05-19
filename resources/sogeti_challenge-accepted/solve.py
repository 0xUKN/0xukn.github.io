#!/usr/bin/python

import socket
import random
import hashlib
from Crypto.Cipher import AES

HOST = 'quals.shadow-league.org'  # The server's hostname or IP address
PORT = 5002       # The port used by the server

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
data = s.recv(4000)
data += s.recv(4000)


ENCRYPTED_CHALLENGE = data.split('\r\n')[-2].split(" ")[-1]
SECRET_KEY = data.split('\r\n')[-3].split(" ")[-1]
KEY_P1,KEY_P2 = SECRET_KEY.split('...') 

print(data)

for j in range(1,10001,1):
	random.seed(j)

	key = 0xffffffff 
	for i in range(10):
	   key ^= random.randint(0x00000000, 0xffffffff)
	secret = hashlib.sha256(str(key))
	data = secret.hexdigest()
	if data[:15] == KEY_P1 and data[-15:] == KEY_P2:
		break

encryption_suite = AES.new(secret.digest(), AES.MODE_CBC, 'LmQHJ6G6QnE5LxbV')
CHALLENGE = encryption_suite.decrypt(ENCRYPTED_CHALLENGE.decode('hex'))
s.send(CHALLENGE + "\n")

data = s.recv(4000)
data += s.recv(4000)
data += s.recv(4000)

print(data)

s.close()
	
