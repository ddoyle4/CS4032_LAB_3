import socket
import sys
import time
import threading

# create a socket object
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 


def read(read_sock):
    while True:
        msg = read_sock.recv(1024)
        print "received:\n%s"%msg

# get local machine name
host = socket.gethostname()                          

port = int(sys.argv[1])

hello="HELO text\n"
kill="KILL_SERVICE\n"
join="JOIN_CHATROOM: mychatroom\nCLIENT_IP: 0\nPORT: 0\nCLIENT_NAME: andrew\n"
leave="LEAVE_CHATROOM: %s\nJOIN_ID: 0\nCLIENT_NAME: andrew\n"
message = "CHAT: %s\nJOIN_ID: 6667\nCLIENT_NAME: andrew\nMESSAGE: %s"

# connection to hostname on the port.
s.connect((host, port))                               

threading.Thread(target=read, args=(s,)).start()
while True:
    cmd = raw_input(">")
    if cmd == "h":
        s.send(hello)
    elif cmd == "k":
        s.send(kill)
    elif cmd == "j":
        s.send(join)
    elif cmd == "l":
        ref = raw_input("enter room ref>")
        msg = leave%ref
        s.send(msg)
    elif cmd == "m":
        ref = raw_input("chat ref:")
        msg = raw_input("message:")
        snd = message%(ref,msg)
        s.send(snd)
    elif cmd== "n":
        pass

s.close()

