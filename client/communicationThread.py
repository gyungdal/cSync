import picamera
import ntplib
import io
import socket
import struct
import json
import enum

from threading import Thread
from time import ctime

@enum.unique
class COMMUNICATION_STATUS(enum.Enum):
    SETUP = 0
    CAMERA_CONFIG = 1
    NTP_SYNC = 2
    IMAGE_SEND = 3
    ERROR = 0xf0
    DONE = 0x0f

class CommunicationThread(Thread):
    def __init__(self, config):
        Thread.__init__(self)
        self.status = COMMUNICATION_STATUS.SETUP
        self.config = config
        self.camera = picamera.PiCamera()
        self.stream = io.BytesIO()
        self.client = socket.socket()
        self.ntp = ntplib.NTPClient()
        self.cameraConfig({
            "width" : 3240,
            "height" : 2494
        })
        self.client.connect((self.config["ip"], self.config["file"]["port"]))
    
    def cameraConfig(self, config):
        self.status = COMMUNICATION_STATUS.CAMERA_CONFIG
        self.camera.resolution(config["width"], config["height"])
        self.camera.led = False
        
    def capture(self):
        try:
            self.status = COMMUNICATION_STATUS.IMAGE_SEND
            connection = self.client.makefile('wb')
            for _ in self.camera.capture_continuous(self.stream, 'png'):
                connection.write(struct.pack('<L', self.stream.tell()))
                connection.flush()
                self.stream.seek(0)
                connection.write(self.stream.read())
                break
            connection.write(struct.pack('<L', 0))
        finally:        
            connection.close()
    
    def getStatus(self):
        return self.status
    
    def run(self):
        while True:
            try:
                data = self.client.recv(1024)
                config = json.loads(data)
                self.status = COMMUNICATION_STATUS.NTP_SYNC
                if "shoot_time" in config.keys():
                    response = self.ntp.request(config['ip'], port=config['ntp']['port'])
                    print(ctime(response.tx_time))        

            except Exception as e:
                self.status = COMMUNICATION_STATUS.ERROR
                print("[ERROR] " + str(e))
                pass
            