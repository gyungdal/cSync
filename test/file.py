import socket
import sys

ip = '127.0.0.1'
port = sys.argv[1]
size = 1024
 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((ip, port))
s.send(bytearray("Hello".encode()))
data = s.recv(size)
 
print(data.decode())
s.close()