import signal 
import logging
from sys import exit
from camera_thread import CameraThread

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
def signalHandler(signum : int, frame):
    logger.critical("Exit Signal %d".format(signum))
    exit()

clients = list()

class DaemonProtocol:
    def load_module(self, module_name : str) -> object:
        logger.info("import module %s".format(module_name))
        return __import__('%s'.format(module_name), fromlist=[module_name])

    def connection_made(self, transport):
        self.transport = transport
        logger.debug("create transport")

    def datagram_received(self, data, addr):
        global clients
        from json import loads
        try:
            decode_data = str(data.decode())
            decode_data = decode_data.replace("'", '"')
            logger.info('decode data : %s' % decode_data)
            message = loads(decode_data)
            logger.debug('Received %r from %s'.format(str(message), addr))
            if hasattr(message, "action"):
                if message["action"] == "handshake":
                    if len(clients) <= 0:
                        thread = self.load_module("camera_thread")["CameraThread"](message["url"])
                        clients.add(thread)
                        thread.start()
        finally:
            pass

    def connection_lost(self, exc):
        logger.error("connection lost %s" % exc)
        self.transport.close()

async def main():
    from asyncio import get_running_loop, sleep
    loop = get_running_loop()
    transport, protocol = await loop.create_datagram_endpoint(
        lambda: DaemonProtocol(),
        local_addr=("0.0.0.0", 8001)
    )

    try:
        await sleep(3600)
    finally:
        logger.error("transport close")
        transport.close()

if __name__ == "__main__":
    from asyncio import run
    signal.signal(signal.SIGINT, signalHandler)
    signal.signal(signal.SIGTERM, signalHandler)
    run(main())