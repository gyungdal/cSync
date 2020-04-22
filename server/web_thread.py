import websockets
from uuid import uuid4
from asyncio import get_event_loop, wait
from pickle import dumps, loads
import logging
from RequestPacket import *
from ResponseHandler import ResponseHandler

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

MAX_PACKET_SIZE = 1024 * 1024 * 1024 
class WebThread(websockets.WebSocketServer):
    def __init__(self, **kwargs):
        ws_protocol = logging.getLogger('websockets.protocol')
        ws_protocol.setLevel(logging.INFO)
        self.handler = ResponseHandler()
        self.HANDLER_MAP = {
            "capture" : self.handler.capture,
            "getId" : self.getIdCheck,
            "status" : self.handler.status,
            "timesync" : self.handler.timesync,
            "setup" : self.handler.setup
        }
        self.kwargs = kwargs
        self.users = dict()

    async def send_command_all(self, command : BasePacket):
        js = command.toJson()
        logger.debug(f"send command all {js}")
        if self.users and command:
            await wait([user.send(js) for user in self.users])

    async def restart(self):
        logger.debug(f"restart")
        await self.send_command_all(RestartPacket())

    async def getIdCheck(self, id : str, packet : dict):
        await self.handler.getId(id, packet)
        if VERSION != packet["version"] :
            ws = [key for key, value in self.users.items() if value == id]
            await ws.send(RestartPacket())

    async def register(self, websocket):
        self.users[websocket] = str(uuid4())
        logger.debug(f"register {self.users[websocket]}")
        packet = SetIdPacket(self.users[websocket])
        await websocket.send(packet.toJson())

    async def unregister(self, websocket):
        logger.debug(f"unregister {self.users[websocket]}")
        del self.users[websocket]

    async def getId(self):
        logger.debug(f"getId")
        await self.send_command_all(GetIdPacket())

    async def status(self):
        logger.debug(f"status")
        await self.send_command_all(StatusPacket())

    async def capture(self):
        logger.debug(f"capture")
        from time import time
        parameter = dict()
        parameter["time"] = ((time() + 5) * 1000)
        parameter["format"] = "png"
        packet = CapturePacket(parameter)
        await self.send_command_all(packet)

    async def setup(self):
        logger.debug(f"setup")
        parameter = {
            "awb_mode" : "auto",
            "brightness" : 50,
            "exif_tags" : {
                "EXIF.UserComments" : 'Copyright (c) 2020 Gyeongsik Kim'
            },
            "exposure_mode" : "auto",
            "flash_mode" : "auto"
        }
        packet = SetupPacket(parameter)
        await self.send_command_all(packet)
    
    async def timesync(self):
        logger.debug(f"timesync")
        packet = TimeSyncPacket()
        await self.send_command_all(packet)
    
    async def prepare(self):
        logger.debug(f"prepare")
        packet = PreparePacket()
        await self.send_command_all(packet)

    async def response(self, websocket, path):
        await self.register(websocket)
        try:
            async for message in websocket:
                packet = loads(message)
                if packet["action"] in self.HANDLER_MAP.keys():
                    await self.HANDLER_MAP[packet["action"]](self.users[websocket], packet)
                else:
                    logger.warning(f"unsupported event: {str(packet)}")
        finally:
            await self.unregister(websocket)
    
    async def server(self, stop):
        logger.debug("server start")
        async with websockets.serve(ws_handler=self.response, host="0.0.0.0", port=8000, write_limit=MAX_PACKET_SIZE, read_limit=MAX_PACKET_SIZE, max_size=MAX_PACKET_SIZE):
            await stop
        logger.debug("server done")