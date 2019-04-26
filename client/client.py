from communication import Communcation
from json import loads, dumps

import ntplib

class Client(Communcation):
    def __init__(self, sck):
        Communcation.__init__(self, sck)
        self.flag = True
        self.ntp = ntplib.NTPClient()
        
    def stop(self):
        self.flag = False
        
    def run(self):
        while self.flag:
            response = loads(self.recv_json())
            response["type"]