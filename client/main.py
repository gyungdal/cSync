# -*- coding: utf8 -*-
import socket
import pickle
import time
import logging
import subprocess
import signal
import sys

class Client():
    def __init__(self):
        self.processList = []
        self.handler = {
            "update" : self.update,
            "update-zip" : self.update,
            "start" : self.start,
            "stop" : self.kill
        }

    def update(self, packet):
        pass
    def start(self, packet):
        pass
    
    def kill(self, packet):
        for process in self.processList :
            process.kill()

    def waitServer(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(('', 8080))
            msg, _ = s.recvfrom(1024)  # 브로드케스트 서버의 전송을 기다린다.
            recv = pickle.loads(msg)
            s.close()
            if recv["service"] == "cSync":
                if recv["command"] in self.handler:
                    self.handler[recv["command"]](recv)

    def dispose(self):
        self.kill()
        
client = Client()

def signalHandler(signum, frame):
    global client
    client.dispose()
    sys.exit()

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signalHandler)
    signal.signal(signal.SIGTERM, signalHandler)
    signal.signal(signal.SIGKILL, signalHandler)
    client = Client()
    while True:
        client.waitServer()