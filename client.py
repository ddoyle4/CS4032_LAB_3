import socket
import sys
import time

# create a socket object
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 

# get local machine name
host = "localhost"                           

port = int(sys.argv[1])

hello="HELO text\n"
kill="KILL_SERVICE\n"
join="JOIN_CHATROOM: [mychatroom]\nCLIENT_IP: [0]\nPORT: [0]\nCLIENT_NAME: [davetherave]\n"


# connection to hostname on the port.
s.connect((host, port))                               
while True:
    cmd = raw_input(">")
    if cmd == "h":
        s.send(hello)
    elif cmd == "k":
        s.send(kill)
    elif cmd == "j":
        s.send(join)
    elif cmd== "n":
        pass

    tm = s.recv(1024)                                     
    print("got this:\n%s"%tm)

s.close()

print("got this:%s"%tm)
