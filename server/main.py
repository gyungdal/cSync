import signal 
import logging
from multiprocessing import Pipe
from web_thread import WebProcess
from sys import exit
from aioconsole import ainput

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def get_broadcast_ip() -> str :
    from sys import platform
    import netifaces as ni
    ifname = "eth0"
    if platform.startswith('darwin'):
        ifname = 'en0'
    ni.ifaddresses(ifname)
    local_ip = ni.ifaddresses(ifname)[ni.AF_INET][0]['addr']
    logger.info("local ip : %s" % local_ip)
    local_ip_split = local_ip.split('.')
    local_ip_split[3] = '255'
    broadcast_ip : str = '.'.join(local_ip_split)
    logger.info("broadcast ip : %s" % broadcast_ip)
    return broadcast_ip


def find_device():
    from json import dumps
    import socket
    message = {}
    message['test'] = "value"
    data = dumps(message)
    broadcast_ip = get_broadcast_ip()
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    logger.debug('send message : %s' % message)
    server.sendto(data.encode(),  (broadcast_ip, 8001))
    server.close()
    return True

def close():
    return False

async def main():
    recv_pipe, send_pipe = Pipe()
    web = WebProcess(send_pipe)
    web.start()
    FLAG = True
    while FLAG:
        MENU = "b : broadcast\nc : shutdown"
        line : str = await ainput(MENU)
        HANDLER = {
            'b' : find_device
        }
        web.send_command()
        line = line.strip().lower()
        if line in HANDLER.keys():
            HANDLER[line]()
        elif line in ['c']:
            FLAG = False
        else:
            logger.warning("no handler : '%s'" % line)


if __name__ == "__main__":
    from asyncio import new_event_loop, set_event_loop
    #signal.signal(signal.SIGKILL, signalHandler)
    loop = new_event_loop()
    set_event_loop(loop)
    def signalHandler(signum, frame):
        logger.critical("Exit Signal %d" % signum)
        exit()

    signal.signal(signal.SIGINT, signalHandler)
    signal.signal(signal.SIGTERM, signalHandler)
    try:
        loop.run_until_complete(main())
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()
        