import signal 
import logging
from sys import exit

logger = logging.getLogger(__name__)
def signalHandler(signum, frame):
    logger.critical("Exit Signal %d".format(signum))
    exit()

def get_ip_address() -> str :
    from sys import platform
    import netifaces as ni
    ifname = "eth0"
    if platform.startswith('darwin'):
        ifname = 'en0'
    ni.ifaddresses(ifname)
    return ni.ifaddresses(ifname)[ni.AF_INET][0]['addr']

def find_device(message : str, broadcast_ip : str):
    import socket
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    logger.debug('send message : %s' % message)
    server.sendto(message.encode(),  (broadcast_ip, 8001))
    server.close()

async def main(broadcast_ip : str):
    from json import dumps
    message = {}
    message['test'] = "value"
    data = dumps(message)
    print(data)
    print(type(data))
    find_device(data, broadcast_ip)

if __name__ == "__main__":
    from asyncio import run
    signal.signal(signal.SIGINT, signalHandler)
    signal.signal(signal.SIGTERM, signalHandler)
    #signal.signal(signal.SIGKILL, signalHandler)
    local_ip = get_ip_address().split('.')
    local_ip[3] = '255'
    broadcast_ip : str = '.'.join(local_ip)
    logger.info("broadcast ip : %s" % broadcast_ip)
    print(broadcast_ip)
    run(main(broadcast_ip))