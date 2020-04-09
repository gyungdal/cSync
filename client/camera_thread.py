import websockets
from threading import Thread
from asyncio import get_event_loop, wait
from pickle import dumps, loads
from io import BytesIO
from base64 import b64encode
import ntplib 
import picamera
from picamera.array import PiRGBArray
from time import time
import logging
import cv2

timeServer = 'time.windows.com' 
logging.basicConfig(level=logging.DEBUG)
class CameraThread(Thread):
    def __init__(self, url, **kwargs):
        Thread.__init__(self)
        self.daemon = True
        self.url = url
        self.loop = get_event_loop()
        self.logger = logging.getLogger(__name__)
        self.parameter = dict()
        self.camera = picamera.PiCamera()
        self.camera.start_preview()

    async def timesync(self, ws, command):
        c = ntplib.NTPClient() 
        response = c.request(timeServer, version=3) 
        self.parameter["timediff"] = response.offset
        self.logger.debug(f"timediff : {response.offset}")

    async def focusing(self, val):
        from os import system
        value = (val << 4) & 0x3ff0
        data1 = (value >> 8) & 0x3f
        data2 = value & 0xf0
        system(f"i2cset -y 1 0x0c {data1} {data2}")
        
    async def sobel(self, img):
        img_gray = cv2.cvtColor(img,cv2.COLOR_RGB2GRAY)
        img_sobel = cv2.Sobel(img_gray,cv2.CV_16U,1,1)
        return cv2.mean(img_sobel)[0]

    async def laplacian(self, img):
        img_gray = cv2.cvtColor(img,cv2.COLOR_RGB2GRAY)
        img_sobel = cv2.Laplacian(img_gray,cv2.CV_16U)
        return cv2.mean(img_sobel)[0]
        
    async def calculation(self):
        rawCapture = PiRGBArray(self.camera) 
        self.camera.capture(rawCapture,format="bgr", use_video_port=True)
        image = rawCapture.array
        rawCapture.truncate(0)
        return await self.laplacian(image)

    async def prepare_capture(self):
        self.camera.resolution = (640, 480)
        self.logger.debug("Start focusing")
	
        max_index = 10
        max_value = 0.0
        last_value = 0.0
        dec_count = 0
        focal_distance = 10
        
        while True:
            await self.focusing(focal_distance)
            val = await self.calculation()
            if val > max_value:
                max_index = focal_distance
                max_value = val
            if val < last_value:
                dec_count += 1
            else:
                dec_count = 0
            if dec_count > 6:
                break
            last_value = val
            focal_distance += 10
            if focal_distance > 1000:
                break
        await self.focusing(max_index)
        self.logger.debug("focusing done")
        self.camera.resolution = (2592,1944)

    async def prepare(self, ws, command):
        await self.prepare_capture()
        command["parameter"]["id"] = self.parameter["id"]
        command["parameter"]["status"] = "done"
        await ws.send(dumps(command))

    async def capture(self, ws, command):
        from lzma import compress
        parameter = command["parameter"]
        #time offset 설정 안돼있으면 설정
        if "timediff" not in self.parameter.keys():
            await self.timesync(ws, command)
        timediff = (self.parameter["timediff"] * 1000)
        stream = BytesIO()
        while (parameter["time"] - timediff) <= (time() * 1000):
            pass
        self.camera.capture(stream, parameter["format"])
        capture_bytes = stream.getvalue()
        compress_capture_bytes = compress(capture_bytes)
        self.logger.info(f"capture : {len(compress_capture_bytes)}bytes, {(len(compress_capture_bytes) / len(capture_bytes)) * 100} % compress") 
        command["parameter"]["data"] = compress_capture_bytes.decode("utf-8")
        await ws.send(dumps(command))
    
    async def setId(self, ws, command):
        if "id" in command["parameter"].keys():
            self.parameter["id"] = command["parameter"]["id"]
        self.logger.info(f"setId : {self.parameter['id']}")

    async def getId(self, ws, command):
        command["parameter"]["id"] = self.parameter["id"]
        self.logger.info(f"getId : {dumps(command)}")
        await ws.send(dumps(command))

    async def setup(self, ws, command):
        parameter = command["parameter"]
        for key in parameter.keys():
            self.logger.info(f"{key} : {parameter[key]}")        
            self.camera[key] = parameter[key]

    async def waitCommand(self):
        FLAG = True
        
        HANDLE = {
            "prepare" : self.prepare,
            "setId" : self.setId,
            "getId" : self.getId,
            "capture" : self.capture,
            "timesync" : self.timesync,
            "setup" : self.setup
        }
        ws = await websockets.connect(self.url)
        ws_protocol = logging.getLogger('websockets.protocol')
        ws_protocol.setLevel(logging.INFO)
        while FLAG:
            command = loads(await ws.recv())
            self.logger.debug(dumps(command))
            if "action" in command.keys():
                await HANDLE[command["action"]](ws, command)

    def run(self):
        from asyncio import run
        run(self.waitCommand())