import websockets
from uuid import uuid4
from threading import Thread
from asyncio import get_event_loop, wait
from json import dumps, loads
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class WebThread(Thread, websockets.WebSocketServer):
    def __init__(self, recv_pipe, **kwargs):
        Thread.__init__(self)
        self.recv_pipe = recv_pipe
        self.kwargs = kwargs
        self.socket = list()
        self.STATE = {"value": 0}
        self.users = dict()

    def state_event(self):
        return dumps({"type": "state", **self.STATE})

    def users_event(self):
        return dumps({"type": "users", "count": len(self.users)})

    async def send_command_all(self, command):
        if self.users and command:
            message = dumps(command)
            await wait([user.send(message) for user in self.users])

    async def register(self, websocket):
        self.users[websocket] = uuid4()
        websocket.send()

    async def unregister(self, websocket):
        del self.users[websocket]
    
    async def echo(self, websocket, path):
        await self.register(websocket)
        try:
            async for message in websocket:
                data : object = loads(message)
                if "action" in data.keys():
                    if data["action"] == "minus":
                        self.STATE["value"] -= 1
                        await self.notify_state()
                    elif data["action"] == "plus":
                        self.STATE["value"] += 1
                        await self.notify_state()
                else:
                    logger.warning("unsupported event: %s" % str(data))
        finally:
            await self.unregister(websocket)
    

    # 여기서 부터는 받아 올때 쓰는 핸들러들
    async def capture(self): 
        pass

    async def timesync(self): 
        pass

    async def setup(self): 
        pass

    async def setId(self): 
        pass

    async def getId(self): 
        pass
    
    async def status(self): 
        pass

    async def version(self): 
        pass

    async def server(self, stop):
        async with websockets.serve(self.echo, "0.0.0.0", 8000):
            await stop

    def run(self):
        from signal import SIGTERM, SIGINT
        loop = get_event_loop()
        stop = loop.create_future()
        loop.add_signal_handler(SIGINT, stop.set_result, None)
        loop.add_signal_handler(SIGTERM, stop.set_result, None)
        try:
            loop.run_until_complete(self.server(stop))
            loop.run_forever()
        finally:
            loop.run_until_complete(loop.shutdown_asyncgens())
            loop.close()