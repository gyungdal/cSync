import queue
import select
import socket
import threading
import sys
import json
import datetime

from os import path, makedirs
from time import sleep

# TODO : 패킷들 정의해서 일반 적인 방식으로 보내도록
class fileServer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)    
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setblocking(0)
        self.server.bind(('0.0.0.0', 0))
        self.server.listen(128)
        self.connections = [self.server]
        self.errors = []
        self.runningFlag = True
        dt = datetime.datetime.now()
        self.path = "{}{}{}_{}{}{}_{}".format(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, dt.microsecond)
        self.clientID = 0
        print(self.server.getsockname())
        
    def __makeFolder(self, path):
        try:
            if not path.isdir(path):
                makedirs(path)
        except OSError as e:
            print("[Error] " + e)
            raise
            
    def getPort(self):
        return self.server.getsockname()[1]

    def stop(self):
        self.runningFlag = False
        
    def sendParam(self, param):
        for item in self.connections:
            if item != self.server:
                item.send(param.toJson())
        
    def run(self):
        while self.connections:
            if not self.runningFlag :
                for item in self.connections:
                    if item != self.server:
                        item.close()
                self.server.close()
                break
            readable, _, _ = select.select(
                self.connections, [], [], 0.1)
            for s in readable:
                if s is self.server:
                    connection, addr = s.accept()
                    connection.setblocking(0)
                    print("[Connect] Client " + str(self.clientID) + " Connected, " + str(addr))
                    self.connections.append(connection)
                    self.clientID += 1
                else:
                    length = int(str(s.recv(128)))
                    if length:
                        recv = json.loads(s.recv(length))
                        print("[Recv] Client " + str(self.connections.index(s)) + " : " + str(len(recv)) + " Bytes")
                        
                    else:
                        print("[Close] Client " + str(s.getsockname()[0]))
                        s.close()
                        self.connections.remove(s)
            