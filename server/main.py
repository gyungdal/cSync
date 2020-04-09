import signal 
import logging
from multiprocessing import Pipe
from web_thread import WebThread
from sys import exit
from aioconsole import ainput

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
def get_local_ip() -> str:
    from sys import platform
    import netifaces as ni
    ifname = "eth0"
    if platform.startswith('darwin'):
        ifname = 'en0'
    ni.ifaddresses(ifname)
    local_ip = ni.ifaddresses(ifname)[ni.AF_INET][0]['addr']
    logger.info(f"local ip : {local_ip}")
    return local_ip

def get_broadcast_ip() -> str :
    local_ip = get_local_ip()
    local_ip_split = local_ip.split('.')
    local_ip_split[3] = '255'
    broadcast_ip : str = '.'.join(local_ip_split)
    logger.info(f"broadcast ip : {broadcast_ip}")
    return broadcast_ip


async def find_device():
    from json import dumps
    import socket
    message = {}
    message['action'] = "handshake"
    message['url'] = (f"ws://{get_local_ip()}:8000")
    data = dumps(message)
    broadcast_ip = get_broadcast_ip()
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    logger.debug(f'send message : {message}')
    server.sendto(data.encode(),  (broadcast_ip, 8001))
    server.close()
    return True

def close():
    return False

async def main(stop, web : WebThread):
    FLAG = True
    while FLAG:
        line : str = await ainput("input command : ")
        HANDLER = {
            'broadcast' : find_device,
            'capture' : web.capture,
            'setup' : web.setup,
            'timesync' : web.timesync,
            'status' : web.status,
            'getId' : web.getId,
            'prepare' : web.prepare
        }
        line = line.strip()
        if line in HANDLER.keys():
            await HANDLER[line]()
        elif line == "exit":
            from os import kill, getpid
            from signal import SIGINT
            kill(getpid(), SIGINT)
        else:
            logger.warning(f"no handler : {line}")


if __name__ == "__main__":
    from asyncio import get_event_loop, gather

    loop = get_event_loop()
    stop = loop.create_future()
    loop.add_signal_handler(signal.SIGINT, stop.set_result, None)
    loop.add_signal_handler(signal.SIGTERM, stop.set_result, None)
    def signalHandler(signum, frame):
        logger.critical(f"Exit Signal {signum}")
        exit()

    signal.signal(signal.SIGINT, signalHandler)
    signal.signal(signal.SIGTERM, signalHandler)

    web = WebThread()
    try:
        tasks = gather(main(stop, web), web.server(stop))
        loop.run_until_complete(tasks)
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()
        