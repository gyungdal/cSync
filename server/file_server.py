import queue
import select
import socket
import threading
import sys
import json
import datetime
import camera_param

from os import path, makedirs
from time import sleep


class fileServer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)    
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setblocking(0)
        self.server.bind(('0.0.0.0', 0))
        self.server.listen(128)
        self.inputs = [self.server]
        self.errors = []
        self.connectList = {}
        self.runningFlag = True
        dt = datetime.datetime.now()
        self.path = "{}{}{}_{}{}{}_{}".format(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, dt.microsecond)
        self.clientID = 0
        print(self.server.getsockname())
    def __makeFolder(self):
        try:
            if not path.isdir(self.path):
                makedirs(self.path)
        except OSError as e:
            print("[Error] " + e)
            raise

            
    def getPort(self):
        return self.server.getsockname()[1]

    def stop(self):
        self.runningFlag = False
        
    def sendParam(self, param):
        for item in self.inputs:
            if item != self.server:
                item.send(param.toJson())
                
    def run(self):
        while self.inputs:
            if not self.runningFlag :
                for item in self.inputs:
                    if item != self.server:
                        item.close()
                        self.connectList[item].close()
                        del self.connectList[item]
                self.server.close()
                break
                
            readable, _, _ = select.select(
                self.inputs, [], [], 0.1)
            for s in readable:
                if s is self.server:
                    connection, addr = s.accept()
                    connection.setblocking(0)
                    connection.write(json.dumps({
                        "id" : self.clientID
                    }))
                    
                    print("[Connect] Client " + str(self.clientID) + " Connected, " + str(addr))
                    self.inputs.append(connection)
                    self.clientID += 1
                else:
                    data = s.recv(1024)
                    if data:
                        print("[Recv] Client " + str(self.inputs.index(s)) + " : " + str(len(data)) + " Bytes")
                        self.connectList[s].write(data)
                    else:
                        print("[Close] Client " + str(s.getsockname()[0]))
                        s.close()
                        self.inputs.remove(s)
                        self.connectList[s].close()
                        del self.connectList[s]
            