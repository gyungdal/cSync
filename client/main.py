# -*- coding: utf8 -*-
from socket import *
import json
import time
import picamera


def capture():
    camera = picamera.PiCamera()
    camera.resolution = (3280, 2464)
    camera.start_preview()
    camera.capture('test.png')
    camera.close()


def waitServer():
    s = socket(AF_INET, SOCK_DGRAM)
    s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    s.bind(('', 8000))
    while True:
        msg, addr = s.recvfrom(1024)  # 브로드케스트 서버의 전송을 기다린다.
        recv = json.loads(msg.decode())
        if recv["service"] == "cSync":
            return recv


if __name__ == "__main__":
    config = waitServer()
    print(config)
    capture()
