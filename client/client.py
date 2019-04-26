from communication import Communcation
from json import loads, dumps
from packet import Packet, PacketType, IDData, StatusData, CaptureSetupData, PhotoData
import ntplib
import picamera

class Client(Communcation):
    def __init__(self, sck):
        Communcation.__init__(self, sck)
        self.flag = True
        self.id = -1
        self.camera = picamera.PiCamera()
        
    def stop(self):
        self.flag = False
        self.camera.close()
        
    def setID(self, id : int):
        self.id = id
    
    def getID(self) -> int:
        return self.id
    
    def __response_id(self):
        data = IDData(self.id)
        packet = Packet(PacketType.RESPONSE_ID, data)
        self.send_json(packet.toJson())
    
    def __response_status(self):
        data = StatusData()
        packet = Packet(PacketType.RESPONSE_STATUS, data)
        self.send_json(packet.toJson())
        
    def __response_capture(self, data):
        config = CaptureSetupData()
        self.camera.resolution(config.width, config.height)
        self.camera.led = False
    
    def run(self):
        while self.flag:
            response = loads(self.recv_json())
            HANDLER_TABLE = {
                PacketType.SET_CLIENT_ID.name : self.setID,
                PacketType.REQUEST_ID.name : self.__response_id,
                PacketType.REQUEST_STATUS.name : self.__response_status,
                PacketType.REQUEST_CAPTURE.name : self.__response_capture,
                PacketType.REQUEST_EXIT.name : self.stop
            }
            if response["type"] in HANDLER_TABLE :
                if "data" in response.key:
                    HANDLER_TABLE[response["type"]](response['data'])
                else:
                    HANDLER_TABLE[response["type"]]()
        