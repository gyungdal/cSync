import socket
import time
import json
from ntp_server import *

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

if __name__ == "__main__":
    ntpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ntpSocket.bind(("0.0.0.0", 0))
    recvThread = RecvThread(ntpSocket)
    recvThread.start()
    workThread = WorkThread(ntpSocket)
    workThread.start()

    broadcast = socket.socket(
        socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    broadcast.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    broadcast.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    broadcast.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
    serverConfig = json.dumps({
        "service": "cSync",
        "ip": get_ip(),
        "file" : {
            "port": 3000
        },
        "ntp" : {
            "port": ntpSocket.getsockname()[1]
        }
    })
    print(serverConfig)
    broadcast.sendto(bytearray(serverConfig.encode()), ("192.168.0.255", 8000))

    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            print("Exiting...")
            recvThread.stop()
            workThread.stop()
            # socket.close()
            print("Exited")
            break
        