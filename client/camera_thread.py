import websockets
from threading import Thread
from asyncio import get_event_loop, wait
from json import dumps, loads
from io import BytesIO
from byte64 import b64encode
import ntplib 
import picamera
import time
import logging

timeServer = 'time.windows.com' 
logging.basicConfig(level=logging.DEBUG)
class CameraThread(Thread):
    def __init__(self, url, **kwargs):
        Thread.__init__(self)
        self.daemon = True
        self.loop = get_event_loop()
        self.logger = logging.getLogger(__name__)
        self.parameter = dict()
        self.camera = picamera.PiCamera()
        self.camera.start_preview()

    async def timesync(self, ws, command):
        c = ntplib.NTPClient() 
        response = c.request(timeServer, version=3) 
        self.parameter["timediff"] = response.offset
        self.logger.debug("timediff : %f" % response.offset)

    async def capture(self, ws, command):
        paramter = command["parameter"]
        stream = BytesIO()
        self.camera.capture(stream, paramter["format"])
        command["parameter"]["data"] = b64encode(stream.getvalue()).decode()
        ws.send(dumps(command))
    
    async def setId(self, ws, command):
        if hasattr(command["parameter"], "id"):
            self.parameter["id"] = command["parameter"]["id"]
        self.logger.info("setId : %s" % self["parameter"]["id"])

    async def getId(self, ws, command):
        command["parameter"]["id"] = self.parameter["id"]
        self.logger.info("getId : %s" % dumps(command))
        ws.send(dumps(command))

    async def setup(self, ws, command):
        parameter = command["parameter"]
        for key in parameter.keys():
            if hasattr(self.camera, key):
                self.camera[key] = parameter[key]

    async def waitCommand(self):
        HANDLE = {
            "setId" : self.setId,
            "getId" : self.getId,
            "capture" : self.capture,
            "timesync" : self.timesync,
            "setup" : self.setup
        }
        async with websockets.connect(self.uri) as websocket:
            command = loads(str(await websocket.recv()))
            if hasattr(command, "action"):
                HANDLE[command["action"]](websocket, command)

    def stop(self):
        self.loop.stop()
        self.loop.run_until_complete(self.loop.shutdown_asyncgens())
        self.loop.close()

    def run(self):
        self.loop.run_until_complete(self.waitCommand())
        self.loop.run_forever()