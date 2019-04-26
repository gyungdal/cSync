from json import dumps, loads
from packet import IDData, Packet, PacketType, SyncData
from time import sleep
from communication import Communcation

class PeerThread(Communcation):
    def __init__(self, socket, id):
        super(socket)
        self.health = True
        self.id = id 

    def stop(self):
        self.health = False
        
    def setClientID(self):
        data = IDData(self.id)
        packet = Packet(PacketType.SET_CLIENT_ID, data)
        data = packet.toJson()
        self.send_json(data)
        
    def requestSync(self) -> SyncData:
        data = IDData(self.id)
        packet = Packet(PacketType.SET_CLIENT_ID, data)
        data = packet.toJson()
        self.send_json(data)
        response = loads(self.recv_json())
        data = loads(response['data'])
        response = SyncData()
        response.loadJson(data)
        return response
        
        
    def run(self):
        while self.health:
            sleep(1)