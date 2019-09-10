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
import RPi.GPIO as GPIO

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
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(5, GPIO.OUT)
        GPIO.setup(6, GPIO.OUT)
        self.setGPIO(True)

    def setGPIO(self, status : bool):
        GPIO.output(5, status)
        GPIO.output(6, status)
             
    def stop(self):
        self.flag = False
        self.camera.close()
        self.close()
        GPIO.cleanup()
        
        
    def setID(self):
        self.id = int(loads(self.response['data'])['id'])
        
    def getID(self) -> int:
        return self.id
    
    def __response_id(self):
        data = IDData(self.id)
        packet = Packet(PacketType.RESPONSE_ID, data)
        self.sendPickle(packet.toPickle())
    
    def __response_status(self):
        data = StatusData()
        response = self.ntp.request(self.config['ip'], port=self.config['port']['ntp'])
        data.diff = response.delay
        data.status = CameraStatus.OK
        packet = Packet(PacketType.RESPONSE_STATUS, data)
        self.sendPickle(packet.toPickle())
        if self.debug : 
            print("[STATUS] Status : {}\tDIFF = {}".format(data.status, data.diff))
        
    def __response_capture(self):
        if self.debug : 
            print("[CAPTURE] Start : {}".format(datetime.now().timestamp()))
        config = CaptureSetupData()
        config.loadPickle(self.response["data"])
        self.camera.resolution = (config.width, config.height)
        self.camera.framerate = 15
        self.camera.led = False
        stream = io.BytesIO()
        result = PhotoData(name=config.name,pt=config.pt)
        self.setGPIO(False)
        while(config.shotTime <= datetime.now().timestamp()):
            continue
        self.setGPIO(True)
        self.camera.capture_continuous(stream, 'png'):
        result.setShotTime(datetime.now().timestamp())
        result.setPhoto(bytearray(stream.getvalue()))
        #시간 데이터 저장
        if self.debug : 
            print("[CAPTURE] Request Time : {}".format(config.shotTime))
            print("[CAPTURE] Capture Time : {}".format(datetime.now().timestamp()))
            
        packet = Packet(PacketType.RESPONSE_CAPTURE, result)
        self.sendPickle(packet.toPickle())
        if self.debug : 
            print("[CAPTURE] Done : {}".format(datetime.now().timestamp()))

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
                self.response = loads(self.recvPickle())
                if self.response["type"] in HANDLER_TABLE.keys() :
                    HANDLER_TABLE[self.response["type"]]()
            except Exception as e:
                if self.debug:
                    print("[ERROR] Thread Exception" + str(e))
                self.stop()
        