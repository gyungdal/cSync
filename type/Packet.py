from PacketType import PacketType
from json import dumps, loads
import enum

class Packet:
    def __init__(self, tp, data):
        self.version = '20190426_dev'
        self.type = tp
        self.data = data

    def toJson(self) -> str:
        return dumps({
            "version": self.version,
            "data": self.data.toJson(),
            "type": self.type.names
        })

    def loadJson(self, json):
        temp = loads(json)
        self.version = temp["version"]
        self.type = PacketType[temp["type"]]
        self.data.loadJson(temp["data"])
