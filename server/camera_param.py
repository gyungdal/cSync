from json import dumps, loads
import enum

class Packet:
    def __init__(self):
        self.version = '20190425_dev'
        self.shoot_time = 0
    
    # timestamp
    def setShootTime(self, when):
        self.shoot_time = when
        
    def toJson(self):
        return dumps({
            "shoot_time" : self.shoot_time,
            "version" : self.version
        })
        
    def loadJson(self, json):
        temp = loads(json)
        self.version = temp["version"]
        self.shoot_time = temp["shoot_time"]
    
class PacketType(enum.Enum):
    GIVE_ID = enum.auto()
    