from threading import Thread
import picamera
import io
import socket
import struct
import json

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
            
    def listener(self):
        while True:
            try:
                data = self.client.recv(1024)
                config = json.loads(data)
                if "shoot_time" in config.keys():
                    
            except Exception as e:
                print("[ERROR] " + str(e))
                pass