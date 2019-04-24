# -*- coding: utf8 -*-
import socket
import json
import time

def waitServer():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('', 8000))
    msg, _ = s.recvfrom(1024)  # 브로드케스트 서버의 전송을 기다린다.
    recv = json.loads(msg.decode())
    s.close()
    if recv["service"] == "cSync":
        return recv
    else:
        return None

if __name__ == "__main__":
    config = None
    while config == None :
        config = waitServer()
    print(config)
