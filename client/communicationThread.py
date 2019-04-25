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
    NTP_SYNC = 1
    CAMERA_SETUP = 2
    IMAGE_SEND = 3
    ERROR = 0xf0
    DONE = 0x0f

class CommunicationThread(Thread):
    def __init__(self, config):
        Thread.__init__(self)
        self.config = config
        
        self.camera = picamera.PiCamera()
        self.camera.resolution(3280, 2464)
        self.camera.led = False
        
        self.stream = io.BytesIO()
        
        self.client = socket.socket()
        self.client.connect((self.config["ip"], self.config["file"]["port"]))
        
        self.ntp = ntplib.NTPClient()
        self.status = COMMUNICATION_STATUS.SETUP
        
    def capture(self):
        try:
            connection = self.client.makefile('wb')
            for _ in self.camera.capture_continuous(self.stream, 'jpeg'):
                connection.write(struct.pack('<L', self.stream.tell()))
                connection.flush()
                self.stream.seek(0)
                connection.write(self.stream.read())
                break
            connection.write(struct.pack('<L', 0))
        finally:        
            connection.close()
    
    def getStatus():
        return self.status
    
    def run(self):
        while True:
            try:
                data = self.client.recv(1024)
                config = json.loads(data)
                if "shoot_time" in config.keys():
                    response = self.ntp.request(config['ip'], port=config['ntp']['port'])
                    print(ctime(response.tx_time))        

            except Exception as e:
                print("[ERROR] " + str(e))
                pass
            