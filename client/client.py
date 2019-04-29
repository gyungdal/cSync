import sys
sys.path.insert(0, '../')
from communication import Communcation
from json import loads, dumps
from packet import Packet, PacketType, IDData, StatusData, CaptureSetupData, PhotoData
from datetime import datetime
import time
import ntplib
import io
class Client(Communcation):
    def __init__(self, sck, config = {}):
        Communcation.__init__(self, sck)
        self.flag = True
        self.id = -1
        self.response = None
        self.camera = picamera.PiCamera()
        
    def stop(self):
        self.flag = False
        self.camera.close()
        self.close()
        
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
        
    def __response_capture(self):
        result = PhotoData()
        config = CaptureSetupData()
        config.loadJson(self.response["data"])
        self.camera.resolution(config.width, config.height)
        self.camera.led = False
        while True:
            if config.shotTime >= datetime.now().timestamp() : # 시간 지나면 작동하게
                stream = io.BytesIO()
                self.camera.capture(stream, 'png')
                result.setPhoto(bytearray(stream.getvalue()))
                #시간 데이터 저장
                self.send_json(result.toJson())
                break

    def run(self):
        HANDLER_TABLE = {
            PacketType.SET_CLIENT_ID.name : self.setID,
            PacketType.REQUEST_ID.name : self.__response_id,
            PacketType.REQUEST_STATUS.name : self.__response_status,
            PacketType.REQUEST_CAPTURE.name : self.__response_capture,
            PacketType.REQUEST_EXIT.name : self.stop
        }
        while self.flag:
            try:
                self.response = loads(self.recv_json())
                if self.response["type"].name in HANDLER_TABLE.keys() :
                    HANDLER_TABLE[self.response["type"].name]()
            except Exception as e:
                print("[ERROR] " + str(e))
        