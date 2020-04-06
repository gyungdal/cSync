import socket
import threading
import logging
import asyncio
import websockets

class Communcation(threading.Thread):
    def __init__(self, sck : socket.socket, debug = False):
        threading.Thread.__init__(self)
        self.socket = sck
        self.debug = debug
        
    def __recvall(self, count : int) -> bytes:
        buf = b''
        while count:
            newbuf = self.socket.recv(count)
            if not newbuf: 
                return None
            buf += newbuf
            count -= len(newbuf)
        return buf
    
    def recvPickle(self) -> bytes:
        while True:
            lenght = int(str(self.__recvall(128), 'utf-8'))
            if lenght > 0 :
                data = self.__recvall(lenght)
                if self.debug:
                    logging.debug("[RECV] LENGTH : " + str(lenght))
                #print("[RECV] DATA : " + data)
                return data
    
    def sendPickle(self, txt : bytes):
        lengthTxt = '{:0128d}'.format(len(txt))
        if self.debug:
            logging.debug("[SEND] LENGTH : " + str(len(txt)))
            logging.debug("[SEND] LENGTH HEADER : " + lengthTxt)
        
        self.socket.sendall(bytes(lengthTxt, 'utf-8'))
        self.socket.sendall(txt)
        
    def close(self):
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()
        
    def run(self):
        pass