#!/usr/bin/python
#coding: utf-8
from z3 import BitVec, Solver, unsat, sat, Or

f = open("solutions_list.txt", "w")

BASE_2 = [0,0,0,0,0,1,0,0,1,1,1,0,1,1,0,0]
BASE_4 = [0,1,0,0,0,1,1,0,0,1,0,0,0,0,0,1]
BASE_6 = [0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,0]
BASE_8 = [0,0,1,1,1,0,0,0,0,0,0,0,0,0,1,0]

s = Solver()
state = [BitVec("state%d" % i, 1) for i in range(64)]
state2 = []
state3 = []
state4 = []

for i in range(16):
	state2.append(state[0 + i] ^ state[1 + i] ^ state[3 + i] ^ state[4 + i])
	s.add(0 ^ (state[0 + i] & state[16 + i]) ^ (state[0 + i] & state[32 + i] & state[48 + i]) ^ (state[16 + i] & state[32 + i] & state[48 + i]) ^ (state[16 + i] & state[32 + i]) ^ (state[16 + i] & state[48 + i]) ^ (state[16 + i]) == BASE_2[i])

state2 = state[16:] + state2
for i in range(16):
	state3.append(state2[0 + i] ^ state2[1 + i] ^ state2[3 + i] ^ state2[4 + i])
	s.add(0 ^ (state2[0 + i] & state2[16 + i]) ^ (state2[0 + i] & state2[32 + i] & state2[48 + i]) ^ (state2[16 + i] & state2[32 + i] & state2[48 + i]) ^ (state2[16 + i] & state2[32 + i]) ^ (state2[16 + i] & state2[48 + i]) ^ (state2[16 + i]) == BASE_4[i])

state3 = state2[16:] + state3
for i in range(16):
	state4.append(state3[0 + i] ^ state3[1 + i] ^ state3[3 + i] ^ state3[4 + i])
	s.add(0 ^ (state3[0 + i] & state3[16 + i]) ^ (state3[0 + i] & state3[32 + i] & state3[48 + i]) ^ (state3[16 + i] & state3[32 + i] & state3[48 + i]) ^ (state3[16 + i] & state3[32 + i]) ^ (state3[16 + i] & state3[48 + i]) ^ (state3[16 + i]) == BASE_6[i])

state4 = state3[16:] + state4
for i in range(16):
	s.add(0 ^ (state4[0 + i] & state4[16 + i]) ^ (state4[0 + i] & state4[32 + i] & state4[48 + i]) ^ (state4[16 + i] & state4[32 + i] & state4[48 + i]) ^ (state4[16 + i] & state4[32 + i]) ^ (state4[16 + i] & state4[48 + i]) ^ (state4[16 + i]) == BASE_8[i])


while s.check() == sat:
	m = s.model()
	out = [str(m[g]) for g in state]
	print("%x" % int(''.join(out),2))
	f.write("%x\n" % int(''.join(out),2))
	newcond = m[state[0]] != state[0]
	for i in range(1,64):
		newcond = Or(newcond,m[state[i]] != state[i])
	s.add(newcond)
	
print("No more solution found.\n")
exit()
