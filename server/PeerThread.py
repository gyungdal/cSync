import socket
import threading
import packet
from time import sleep

class PeerThread(threading.Thread):
    def __init__(self, socket, id):
        self.socket = socket
        self.health = True
        self.id = id 
    
    def stop(self):
        self.health = False
        
    def setClientID(self):
        data = acket.IDData()
        packet = packet(packet.PacketType.SET_CLIENT_ID)
        packet
    def run(self):
        while self.health:
            sleep(1)