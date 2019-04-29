import queue
import select
import socket
import threading
import sys
import json
import datetime

from os import path, makedirs
from time import sleep

from json import dumps, loads
from packet import IDData, Packet, PacketType, SyncData, CameraStatus, PhotoData, CaptureSetupData
from communication import Communcation

class PeerThread(Communcation):
    def __init__(self, sck, id):
        Communcation.__init__(self, sck)
        self.flag = True
        self.id = id 
        self.delay = 0
        self.status = CameraStatus.DISCONNECTED

    def stop(self):
        self.flag = False
        self.close()
        
    def setClientID(self):
        data = IDData(self.id)
        packet = Packet(PacketType.SET_CLIENT_ID, data)
        data = packet.toJson()
        self.send_json(data)
        
    def requestSync(self):
        data = IDData(self.id)
        packet = Packet(PacketType.SET_CLIENT_ID, data)
        data = packet.toJson()
        self.send_json(data)
        response = loads(self.recv_json())
        data = loads(response['data'])
        response = SyncData()
        response.loadJson(data)
        self.status = response.status
        self.delay = response.delay
        print("[INFO] Client {} Status\n\tDelay : {}\nStatus : {}"
              .format(self.id, self.delay, self.status.name))
    
    def capture(self, when : float, pt : str) :
        if self.status == CameraStatus.OK:
            data = CaptureSetupData(shotTime = when + self.delay)
            packet = Packet(PacketType.REQUEST_CAPTURE, data)
            data = packet.toJson()
            self.send_json(data)
            response = loads(self.recv_json())
            data = loads(response['data'])
            photo = PhotoData()
            photo.loadJson(data)
            photo.savePhoto(pt, "{}.png".format(self.id))
            print("[INFO] Save Image {}.png".format(self.id))
         
    def run(self):
        self.setClientID()
        self.requestSync()
        while self.flag:
            sleep(1)
            
# TODO : 패킷들 정의해서 일반 적인 방식으로 보내도록
class fileServer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)    
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(('0.0.0.0', 0))
        self.server.listen(128)
        self.peers = []
        self.runningFlag = True
        self.clientID = 0
        print("[INFO] File Server Start\n\tㄴ{}".format(self.server.getsockname()))
        
    def __makeFolder(self, path):
        try:
            if not path.isdir(path):
                makedirs(path)
                print("[ALERT] Make Folder {}".format(path))
        except OSError as e:
            print("[Error] " + e)
            raise
            
    def capture(self):
        dt = datetime.datetime.now() + datetime.timedelta(seconds=5)
        경로 = "{}{}{}_{}{}{}_{}".format(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, dt.microsecond)
        self.__makeFolder(경로)
        for peer in self.peers:
            peer.capture(when=dt.timestamp(), pt=경로)
    
    def getStatus(self):
        for peer in self.peers:
            peer.requestSync()
    
    def getPort(self):
        return self.server.getsockname()[1]

    def stop(self):
        self.runningFlag = False
    
    def run(self):
        while self.runningFlag:
            connection, addr = self.server.accept()
            print("[Connect] Client " + str(self.clientID) + " Connected, " + str(addr))
            peer = PeerThread(connection, self.clientID)
            self.clientID = self.clientID + 1
            self.peers.append(peer)
        for item in self.peers:
            item.stop()
        self.server.close()