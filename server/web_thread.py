import websockets
from multiprocessing import Process, Pipe
from asyncio import get_event_loop, wait
from json import dumps, loads
class WebProcess(Process, websockets.WebSocketServer):
    def __init__(self, pipe, **kwargs):
        super(WebProcess, self).__init__()
        self.pipe = pipe
        self.kwargs = kwargs
        self.socket = list()
        self.STATE = {"value": 0}
        self.USERS = set()


    def state_event(self):
        return dumps({"type": "state", **self.STATE})


    def users_event(self):
        return dumps({"type": "users", "count": len(self.USERS)})


    async def notify_state(self):
        if self.USERS:  # asyncio.wait doesn't accept an empty list
            message = self.state_event()
            await wait([user.send(message) for user in self.USERS])


    async def notify_users(self):
        if self.USERS:  # asyncio.wait doesn't accept an empty list
            message = self.users_event()
            await wait([user.send(message) for user in self.USERS])


    async def register(self, websocket):
        self.USERS.add(websocket)
        await self.notify_users()


    async def unregister(self, websocket):
        self.USERS.remove(websocket)
        await self.notify_users()

    async def echo(self, websocket, path):
        await self.register(websocket)
        try:
            await websocket.send(self.state_event())
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
                    print("unsupported event: %s" % str(data))
        finally:
            await self.unregister(websocket)
            
    async def server(self, stop):
        async with websockets.serve(self.echo, "0.0.0.0", 8000):
            await stop

    def run(self):
        from signal import SIGTERM
        loop = get_event_loop()
        stop = loop.create_future()
        loop.add_signal_handler(SIGTERM, stop.set_result, None)
        loop.run_until_complete(self.server(stop))
        loop.run_forever()

parent_conn, child_conn = Pipe()
web = WebProcess(child_conn)
web.start()
web.join()