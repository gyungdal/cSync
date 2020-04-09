import signal 
import logging
from sys import exit

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
def signalHandler(signum : int, frame):
    logger.critical("Exit Signal %d" % signum)
    exit()

clients = list()

class DaemonProtocol:
    def load_module(self, module_name : str, class_name : str):
        logger.info("import module {0} : {1}".format(module_name, class_name))
        temp = __import__(module_name, fromlist=[module_name])
        return getattr(temp, class_name)

    def connection_made(self, transport):
        self.transport = transport
        logger.debug("create transport")

    def datagram_received(self, data, addr):
        global clients
        from json import loads
        try:
            decode_data = str(data.decode())
            decode_data = decode_data.replace("'", '"')
            logger.info('decode data : {0}'.format(decode_data))
            message = loads(decode_data)
            logger.debug('Received {0} from {1}'.format(str(message), addr))
            if "action" in message.keys():
                if message["action"] == "handshake":
                    if len(clients) <= 0:
                        thread = self.load_module("camera_thread", "CameraThread")(message["url"])
                        clients.append(thread)
                        thread.start()
                        
        finally:
            pass

    def connection_lost(self, exc):
        logger.error("connection lost {0}".format(exc))
        self.transport.close()

async def main():
    global clients
    from asyncio import get_running_loop, sleep
    loop = get_running_loop()
    transport, protocol = await loop.create_datagram_endpoint(
        lambda: DaemonProtocol(),
        local_addr=("0.0.0.0", 8001)
    )

    try:
        for client in clients:
            if client.isAlive():
                client.handled = True
        clients = [t for t in clients if not t.handled]
        logger.info(f"Client Count : {len(clients)}")
        await sleep(1)
    finally:
        logger.error("transport close")
        transport.close()

if __name__ == "__main__":
    from asyncio import run
    signal.signal(signal.SIGINT, signalHandler)
    signal.signal(signal.SIGTERM, signalHandler)
    run(main())