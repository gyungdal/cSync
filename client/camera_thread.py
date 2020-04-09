import websockets
from threading import Thread
from asyncio import get_event_loop, wait
from json import dumps, loads
from io import BytesIO
from base64 import b64encode
import ntplib 
import picamera
from time import time
import logging

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

    async def capture(self, ws, command):
        parameter = command["parameter"]
        #time offset 설정 안돼있으면 설정
        if "timediff" not in self.parameter.keys():
            await self.timesync(ws, command)
        timediff = (self.parameter["timediff"] * 1000)
        stream = BytesIO()
        while (parameter["time"] - timediff) <= (time() * 1000):
            pass
        self.camera.capture(stream, parameter["format"])
        command["parameter"]["data"] = b64encode(stream.getvalue()).decode()
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
            self.camera[key] = parameter[key]

    async def waitCommand(self):
        FLAG = True
        
        HANDLE = {
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
            command = loads(str(await ws.recv()))
            self.logger.debug(dumps(command))
            if "action" in command.keys():
                await HANDLE[command["action"]](ws, command)

    def run(self):
        from asyncio import run
        run(self.waitCommand())