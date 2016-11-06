import socket
import sys
import time

# create a socket object
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 

# get local machine name
host = "localhost"                           

port = int(sys.argv[1])

# connection to hostname on the port.
s.connect((host, port))                               
while True:
    s.send("HELOaskdujhaskdjfhfn\n")
    # Receive no more than 1024 bytes
    tm = s.recv(1024)                                     
    print("got this:%s"%tm)
    time.sleep(3)

s.close()

print("got this:%s"%tm)
