# -*- coding: utf8 -*-
from socket import *
import json

def sendServerInfo(port):
    s = socket(AF_INET, SOCK_DGRAM)
    s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1) # BC 지원 옵션
    data = json.dumps({
        "service" : "cSync",
        "ip" : gethostbyname(gethostname()),
        "port" : port
    })
    s.sendto(data, ('192.168.3.255',8000))

s = socket()
s.bind(('',0))
sendServerInfo(s.getsockname()[1])
