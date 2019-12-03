

import numpy as py
import cv2
import RPi.GPIO as GPIO
import picamera
import socket
import io
import ntplib
import time
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from datetime import datetime
from packet import Packet, PacketType, IDData, StatusData, CaptureSetupData, PhotoData, CameraStatus
from pickle import loads, dumps
from communication import Communcation

try:
    import picamera
    from picamera.array import PiRGBArray
except:
    sys.exit(0)
    
class Sub(Communcation):
    def __init__(self, ip : str, port : int, debug=False):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(5, GPIO.OUT)
        GPIO.setup(6, GPIO.OUT)
        sck = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sck.connect(ip, port)
        Communcation.__init__(self, sck, debug=debug)
        self.flag = True
        self.id = -1
        self.response = None
        self.debug = debug
        self.camera = picamera.PiCamera()
        self.offset = 0
        self.setGPIO(True)

    def focusing(self, val):
        value = (val << 4) & 0x3ff0
        data1 = (value >> 8) & 0x3f
        data2 = value & 0xf0
        os.system("i2cset -y 0 0x0c %d %d" % (data1, data2))

    def sobel(self, img):
        img_gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        img_sobel = cv2.Sobel(img_gray, cv2.CV_16U, 1, 1)
        return cv2.mean(img_sobel)[0]

    def laplacian(self, img):
        img_gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        img_sobel = cv2.Laplacian(img_gray, cv2.CV_16U)
        return cv2.mean(img_sobel)[0]

    def calculation(self, camera):
        rawCapture = PiRGBArray(camera)
        camera.capture(rawCapture, format="bgr", use_video_port=True)
        image = rawCapture.array
        rawCapture.truncate(0)
        return self.laplacian(image)

    def setGPIO(self, status: bool):
        GPIO.output(5, status)
        GPIO.output(6, status)

    def stop(self):
        self.flag = False
        self.camera.stop_preview()
        self.camera.close()
        self.close()
        GPIO.cleanup()
    
    def __ntpUpdate(self):
        timeServer = "pool.ntp.org"
        c = ntplib.NTPClient()
        response = c.request(timeServer, version=3)
        self.offset = response.offset


    def __cameraPrepare(self):
        self.camera.resolution = (640, 480)
        print("Start focusing")
        max_index = 10
        max_value = 0.0
        last_value = 0.0
        dec_count = 0
        focal_distance = 10

        while True:
            # Adjust focus
            self.focusing(focal_distance)
            # Take image and calculate image clarity
            val = self.calculation(self.camera)
            # Find the maximum image clarity
            if val > max_value:
                max_index = focal_distance
                max_value = val

            # If the image clarity starts to decrease
            if val < last_value:
                dec_count += 1
            else:
                dec_count = 0
            # Image clarity is reduced by six consecutive frames
            if dec_count > 6:
                break
            last_value = val

            # Increase the focal distance
            focal_distance += 10
            if focal_distance > 1000:
                break

        # Adjust focus to the best
        self.focusing(max_index)
        print("max index = %d,max value = %lf" % (max_index, max_value))

    def __cameraStatus(self):
        self.camera.resoulution = (self.response.width, self.response.height)
        self.camera.framerate = 15
        self.camera.led = False
        self.awb_mode = self.response.awb_mode
        self.exposure_mode = self.response.exposure_mode
        self.image_effect = self.response.image_effect
        self.brightness = self.response.brightness

        data = StatusData()
        
        data.diff = response.delay
        data.status = CameraStatus.OK
        packet = Packet(PacketType.RESPONSE_STATUS, data)
        self.sendPickle(packet.toPickle())
        if self.debug:
            print("[STATUS] Status : {}\tDIFF = {}".format(
                data.status, data.diff))

    def __cameraCapture(self):
        if self.debug:
            print("[CAPTURE] Start : {}".format(datetime.now().timestamp()))
        self.camera.resolution = (config.width, config.height)
        self.camera.framerate = 15
        self.camera.led = False
        stream = io.BytesIO()
        result = PhotoData(name=config.name, pt=config.pt)
        while(config.shotTime <= datetime.now().timestamp()):
            continue
        self.setGPIO(False)
        self.camera.capture(stream, 'png')
        self.setGPIO(True)
        result.setShotTime(datetime.now().timestamp())
        result.setPhoto(bytearray(stream.getvalue()))
        # 시간 데이터 저장
        if self.debug:
            print("[CAPTURE] Request Time : {}".format(config.shotTime))
            print("[CAPTURE] Capture Time : {}".format(
                datetime.now().timestamp()))

        packet = Packet(PacketType.RESPONSE_CAPTURE, result)
        self.sendPickle(packet.toPickle())
        if self.debug:
            print("[CAPTURE] Done : {}".format(datetime.now().timestamp()))


    def run(self):
        HANDLER_TABLE = {
            "ntp" : {
                "update" : self.__ntpUpdate
            },
            "camera" : {
                "prepare" : self.__cameraPrepare,
                "status" : self.__cameraStatus,
                "capture" : self.__cameraCapture
            }
        }
        while self.flag:
            try:
                self.response = loads(self.recvPickle())
                if self.response["service"] in HANDLER_TABLE.keys():
                    if self.response["command"] in HANDLER_TABLE[self.response["service"]].keys():
                        HANDLER_TABLE[self.response["service"]][self.response["command"]]()
            except Exception as e:
                if self.debug:
                    print("[ERROR] Thread Exception" + str(e))
                self.stop()
