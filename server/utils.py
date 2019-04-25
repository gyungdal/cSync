import socket 
import json

class Utils:
    def __init__(self):
        pass
    
    def getIp(self):
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

    def hereAmI(self, fileServerPort, ntpPort):
        broadcast = socket.socket(
            socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        broadcast.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        broadcast.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        broadcast.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        serverConfig = json.dumps({
            "service": "cSync",
            "ip": self.getIp(),
            "file" : {
                "port": fileServerPort
            },
            "ntp" : {
                "port": ntpPort
            }
        })
        print(serverConfig)
        broadcast.sendto(bytearray(serverConfig.encode()), ("192.168.0.255", 8000))
        broadcast.close()