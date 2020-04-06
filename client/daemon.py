import signal 
import logging
from sys import exit

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
def signalHandler(signum : int, frame):
    logger.critical("Exit Signal %d".format(signum))
    exit()

class DaemonProtocol:
    def load_module(self, module_name : str) -> object:
        logger.info("import module %s".format(module_name))
        return __import__('%s'.format(module_name), fromlist=[module_name])

    def connection_made(self, transport):
        self.transport = transport
        logger.debug("create transport")

    def datagram_received(self, data, addr):
        from json import loads
        decode_data = str(data.decode())
        decode_data = decode_data.replace("'", '"')
        logger.info('decode data : %s' % decode_data)
        message = loads(decode_data)
        logger.debug('Received %r from %s'.format(str(message), addr))
    
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
        await sleep(3600) #serve 3600 seconds
    finally:
        logger.error("transport close")
        transport.close()

if __name__ == "__main__":
    from asyncio import run
    signal.signal(signal.SIGINT, signalHandler)
    signal.signal(signal.SIGTERM, signalHandler)
    #signal.signal(signal.SIGKILL, signalHandler)
    run(main())