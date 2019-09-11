import numpy as py
import cv2
import RPi.GPIO as GPIO
import picamera
import socket
import io
import ntplib
import time
from datetime import datetime
from packet import Packet, PacketType, IDData, StatusData, CaptureSetupData, PhotoData, CameraStatus
from pickle import loads, dumps
from communication import Communcation
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

try:
    import picamera
    from picamera.array import PiRGBArray
except:
    sys.exit(0)


class Client(Communcation):
    def __init__(self, config={}, debug=False):
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
        return laplacian(image)

    def setGPIO(self, status: bool):
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
        response = self.ntp.request(
            self.config['ip'], port=self.config['port']['ntp'])
        data.diff = response.delay
        camera = picamera.PiCamera()
        # open camera preview
        camera.start_preview()
        # set camera resolution to 640x480(Small resolution for faster speeds.)
        camera.resolution = (640, 480)

        print("Start focusing")

        max_index = 10
        max_value = 0.0
        last_value = 0.0
        dec_count = 0
        focal_distance = 10

        while True:
            # Adjust focus
            focusing(focal_distance)
            # Take image and calculate image clarity
            val = calculation(camera)
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
        focusing(max_index)
        time.sleep(1)
        # set camera resolution to 2592x1944
        camera.resolution = (2592, 1944)
        # save image to file.
        camera.capture("test.jpg")
        print("max index = %d,max value = %lf" % (max_index, max_value))
        # while True:
        #	time.sleep(1)

        camera.stop_preview()
        camera.close()
        data.status = CameraStatus.OK
        packet = Packet(PacketType.RESPONSE_STATUS, data)
        self.sendPickle(packet.toPickle())
        if self.debug:
            print("[STATUS] Status : {}\tDIFF = {}".format(
                data.status, data.diff))

    def __response_capture(self):
        if self.debug:
            print("[CAPTURE] Start : {}".format(datetime.now().timestamp()))
        config = CaptureSetupData()
        config.loadPickle(self.response["data"])
        self.camera.resolution = (config.width, config.height)
        self.camera.framerate = 15
        self.camera.led = False
        stream = io.BytesIO()
        result = PhotoData(name=config.name, pt=config.pt)
        self.setGPIO(False)
        while(config.shotTime <= datetime.now().timestamp()):
            continue
        self.setGPIO(True)
        self.camera.capture(stream, 'png')
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
            PacketType.SET_CLIENT_ID.name: self.setID,
            PacketType.REQUEST_ID.name: self.__response_id,
            PacketType.REQUEST_STATUS.name: self.__response_status,
            PacketType.REQUEST_CAPTURE.name: self.__response_capture,
            PacketType.REQUEST_EXIT.name: self.stop
        }
        while self.flag:
            try:
                self.response = loads(self.recvPickle())
                if self.response["type"] in HANDLER_TABLE.keys():
                    HANDLER_TABLE[self.response["type"]]()
            except Exception as e:
                if self.debug:
                    print("[ERROR] Thread Exception" + str(e))
                self.stop()
