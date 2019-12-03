# -*- coding: utf8 -*-
import socket
import pickle
import time
import logging
import subprocess
import signal
import sys
import enum

from client.communication import Communcation
from client.packet import *

class Client(Communcation):
    def __init__(self):
        self.sourcePath = os.path.dirname(os.path.abspath(__file__))
        self.cameraSourcePath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bin")
        self.processList = []
        self.handlerTable = {
            CommandType.START : self.start,
            CommandType.UPDATE : self.update,
            CommandType.UPDATE_ZIP : self.updateZip,
            CommandType.KILL : self.kill
        }

    def update(self, data : UpdatePacket):
        self.kill(None)
        from urllib.request import urlopen
        response = urlopen(data.url)
        zip = UpdateZIPPacket()
        zip.file = response.read()
        self.updateZip(zip)

    def updateZip(self, data : UpdateZIPPacket):
        self.kill(None)
        from zipfile import ZipFile
        from shutil import rmtree
        from os import chdir
        rmtree(cameraSourcePath)
        chdir(cameraSourcePath)
        with ZipFile(data.file) as zip:
            zip.printdir()
            zip.extractall()

    def start(self, data : StartPacket):
        from os import chdir
        chdir(cameraSourcePath)
        proc = subprocess.Popen(["python3.7", "sub.py", data.ip, data.port])
        self.processList.append(proc)
    
    def kill(self, data):
        for process in self.processList :
            process.kill()

    def waitServer(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(('', 8080))
            msg, _ = s.recvfrom(1024)  # 브로드케스트 서버의 전송을 기다린다.
            packet = Packet()
            packet.loadPickle(msg)
            s.close()
            if packet.sendTo is ParserType.CLIENT :
                if packet.service is ServiceType.CSYNC :
                    if packet.command in self.handlerTable.keys():
                        self.handlerTable[packet.command](packet.data)

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
    while True:
        client.waitServer()