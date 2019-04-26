import socket
import threading

class Communcation(threading.Thread):
    def __init__(self, socket):
        threading.Thread.__init__(self)
        self.socket = socket
        
    def __recvall(self, count) -> bytearray:
        buf = b''
        while count:
            newbuf = self.socket.recv(count)
            if not newbuf: 
                return None
            buf += newbuf
            count -= len(newbuf)
        return buf
    
    def recv_json(self) -> str:
        while True:
            lenght = int(self.socket.recv(128))
            if lenght > 0 :
                return self.__recvall(lenght).decode('utf8')
    
    def send_json(self, txt):
        lengthTxt = '{:0128d}'.format(len(txt))
        self.socket.sendall(lengthTxt)
        self.socket.sendall(txt)
        
    def run(self):
        pass