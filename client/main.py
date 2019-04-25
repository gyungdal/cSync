# -*- coding: utf8 -*-
import socket
import json
import time
import ntplib
from time import ctime
# https://picamera.readthedocs.io/en/release-1.13/recipes1.html

def waitServer():
    try:
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
    except Exception as e:
        print("[ERROR] : Server broadcast data crash")
        print("\tㄴ Description -> " + e)
        return None
    
if __name__ == "__main__":
    try: 
        while True:
            config = None
            while config == None :
                config = waitServer()
            print(config)
            c = ntplib.NTPClient()
            response = c.request(config['ip'], port=config['ntp']['port'])
            print(ctime(response.tx_time))
    except Exception as ex: # 에러 종류
        print('[ERROR] : ', ex)