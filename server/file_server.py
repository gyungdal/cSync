import queue
import select
import socket
import threading
import sys
import datetime

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
            if e.errno != EEXIST:
                print("Failed to create directory!!!!!")
                raise

            
    def getPort(self):
        return self.server.getsockname()[1]

    def stop(self):
        self.runningFlag = False
    def run(self):
        while self.inputs:
            if not self.runningFlag :
                for item in self.inputs:
                    if item != self.server:
                        item.close()
                        self.connectList.close()
                        del self.connectList[item]
                self.server.close()
                break
                
            readable, _, _ = select.select(
                self.inputs, [], [], 0.1)
            for s in readable:
                if s is self.server:
                    connection, _ = s.accept()
                    connection.setblocking(0)
                    self.inputs.append(connection)
                    self.connectList[connection] = open(path.join(self.path, "{}.png".format(self.clientID)), "wb")
                else:
                    data = s.recv(1024)
                    if data:
                        print("[RECV " + str(self.inputs.index(s)) + "] " + str(data))
                        self.connectList[s].write(data)
                    else:
                        self.inputs.remove(s)
                        s.close()
                        self.connectList[s].close()
                        del self.connectList[s]
            