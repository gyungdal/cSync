import socket
import threading

class Communcation(threading.Thread):
    def __init__(self, sck : socket.socket):
        threading.Thread.__init__(self)
        self.socket = sck
        
    def __recvall(self, count : int) -> bytearray:
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
            lenght = int(self.__recvall(128))
            if lenght > 0 :
                data = self.__recvall(lenght).decode('utf-8')
                print("[RECV] LENGTH : " + str(lenght))
                #print("[RECV] DATA : " + data)
                return data
    
    def send_json(self, txt : str):
        lengthTxt = '{:0128d}'.format(len(txt))
        print("[SEND] LENGTH : " + str(len(txt)))
        print("[SEND] LENGTH HEADER : " + lengthTxt)
        print("[SEND] TXT : " + txt)
        
        self.socket.sendall(bytearray(lengthTxt, 'utf-8'))
        self.socket.sendall(bytearray(txt, 'utf-8'))
        
    def close(self):
        self.socket.close()
        
    def run(self):
        pass