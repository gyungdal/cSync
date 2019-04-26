import enum

from json import dumps, loads
from base64 import b64encode
from datetime import datetime

class PacketType(enum.Enum):
    NONE = enum.auto()
    
    SET_CLIENT_ID = enum.auto()
    
    REQUEST_ID = enum.auto()
    RESPONSE_ID = enum.auto()
    
    REQUEST_SYNC = enum.auto()
    SYNC_DATA = enum.auto()
    
    CAMERA_SETUP = enum.auto()
    PHOTO_DATA = enum.auto()
    
    REQUEST_EXIT = enum.auto()
    
class CameraStatus(enum.Enum):
    OK = enum.auto()
    
    BUSY = enum.auto()
    DISCONNECTED = enum.auto()
    
class BaseData:
    def toJson(self) -> str:
        pass

    def loadJson(self, txt):
        pass
    
class Packet:
    def __init__(self, tp : PacketType, data : BaseData):
        self.version = '20190426_dev'
        self.type = tp
        self.data = data

    def getType(self) -> PacketType:
        return self.type
        
    def setType(self, tp):
        self.type = tp
        
    def setData(self, data):
        self.data = data
        
    def getData(self):
        return self.data
    
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

class CameraSetupData(BaseData):
    def __init__(self, width = 3240, height = 2494, shotTime = datetime.now()):
        self.width = width
        self.height = height
        self.shotTime = shotTime
        
    def toJson(self) -> str:
        return dumps({
            "width" : self.width,
            "height" : self.height,
            "shotTime" : self.shotTime
        })
        
    def loadJson(self, txt):
        data = loads(txt)
        self.shotTime = data["shotTime"]
        self.width = data["width"]
        self.height = data["height"]
        
class IDData(BaseData):
    def __init__(self, id = 0):
        self.id = id
        
    def toJson(self) -> str:
        return dumps({
            "id" : id
        })
        
    def loadJson(self, txt):
        self.id = loads(txt)["id"]
        
        
class PhotoData(BaseData):
    def __init__(self, photo):
        self.id = id
        self.photo = photo
        
    def toJson(self) -> str:
        return dumps({
            "photo" : b64encode(self.photo)
        })
        
    def loadJson(self, txt):
        data = loads(txt)
        self.photo = data["photo"]
        
class SyncData(BaseData):
    def __init__(self, diff = 0, status = CameraStatus.DISCONNECTED):
        self.diff = diff
        self.status = status
        
    def toJson(self) -> str:
        return dumps({
            "diff" : self.diff,
            "status" : self.status
        })
        
    def loadJson(self, txt):
        data = loads(txt)
        self.diff = data["diff"]
        self.status = data["status"]