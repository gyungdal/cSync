from json import dumps, loads
from ../packet import IDData, Packet, PacketType, SyncData
from time import sleep
from communication import Communcation

class PeerThread(Communcation):
    def __init__(self, sck, id):
        Communcation.__init__(self, sck)
        self.flag = True
        self.id = id 

    def stop(self):
        self.flag = False
        self.close()
        
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
        while self.flag:
            sleep(1)