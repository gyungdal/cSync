import socket
import time
import json

broadcast = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
broadcast.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
broadcast.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
broadcast.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
serverConfig = json.dumps({
    "service" : "cSync",
    "ip" : socket.gethostbyname(socket.gethostname()),
    "port" : 3000
})
broadcast.sendto(bytearray(serverConfig.encode()), ("192.168.0.255", 8000))