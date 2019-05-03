import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from communication import Communcation
from pickle import loads, dumps
from packet import Packet, PacketType, IDData, StatusData, CaptureSetupData, PhotoData, CameraStatus
from datetime import datetime
import time
import ntplib
import io
import socket
import picamera

class Client(Communcation):
    def __init__(self, config = {}, debug=False):
        sck = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sck.connect((config['ip'], config['port']['file']))
        Communcation.__init__(self, sck, debug=debug)
        self.flag = True
        self.id = -1
        self.ntp = ntplib.NTPClient()
        self.response = None
        self.camera = picamera.PiCamera()
        self.config = config
        self.debug = debug
        
    def stop(self):
        self.flag = False
        self.camera.close()
        self.close()
        
        
    def setID(self):
        self.id = int(loads(self.response['data'])['id'])
        
    def getID(self) -> int:
        return self.id
    
    def __response_id(self):
        data = IDData(self.id)
        packet = Packet(PacketType.RESPONSE_ID, data)
        self.send_json(packet.toJson())
    
    def __response_status(self):
        data = StatusData()
        response = self.ntp.request(self.config['ip'], port=self.config['port']['ntp'])
        data.diff = response.delay
        data.status = CameraStatus.OK
        packet = Packet(PacketType.RESPONSE_STATUS, data)
        self.send_json(packet.toJson())
        
    def __response_capture(self):
        config = CaptureSetupData()
        config.loadJson(self.response["data"])
        self.camera.resolution = (config.width, config.height)
        self.camera.framerate = 15
        self.camera.led = False
        stream = io.BytesIO()
        result = PhotoData(name=config.name,pt=config.pt)
        for _ in self.camera.capture_continuous(stream, 'png'):
            if config.shotTime <= datetime.now().timestamp() : # 시간 지나면 작동하게
                result.setShotTime(datetime.now().timestamp())
                result.setPhoto(bytearray(stream.getvalue()))
                break
        #시간 데이터 저장
        packet = Packet(PacketType.RESPONSE_CAPTURE, result)
        self.send_json(packet.toJson())

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
                if self.response["type"] in HANDLER_TABLE.keys() :
                    HANDLER_TABLE[self.response["type"]]()
            except Exception as e:
                if self.debug:
                    print("[ERROR] Thread Exception" + str(e))
                self.stop()
        