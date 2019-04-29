import enum

from json import dumps, loads
import os
from base64 import b64encode, b64decode
from datetime import datetime

class PacketType(enum.Enum):
    NONE = enum.auto()
    
    SET_CLIENT_ID = enum.auto()
    
    REQUEST_ID = enum.auto()
    RESPONSE_ID = enum.auto()
    
    REQUEST_STATUS = enum.auto()
    RESPONSE_STATUS = enum.auto()
    
    REQUEST_CAPTURE = enum.auto()
    RESPONSE_CAPTURE = enum.auto()
    
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
    def __init__(self, tp : PacketType, data):
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
            "type": PacketType[self.type]
        })

    def loadJson(self, json):
        temp = loads(json)
        self.version = temp["version"]
        self.type = PacketType[temp["type"]]
        TABLE = {
            PacketType.SET_CLIENT_ID.name : IDData(),
            PacketType.REQUEST_ID.name : None,
            PacketType.RESPONSE_ID.name : IDData(),
            PacketType.REQUEST_STATUS.name : None,
            PacketType.RESPONSE_STATUS.name : StatusData(),
            PacketType.REQUEST_CAPTURE.name : CaptureSetupData(),
            PacketType.RESPONSE_CAPTURE.name : PhotoData(),
            PacketType.REQUEST_EXIT.name : None
        }
        self.data = TABLE[temp['type']]
        if self.data != None:
            self.data.loadJson(temp["data"])
        
class IDData(BaseData):
    def __init__(self, id = 0):
        self.id = id
        
    def toJson(self) -> str:
        return dumps({
            "id" : self.id
        })
        
    def loadJson(self, txt):
        self.id = loads(txt)["id"]
        
class CaptureSetupData(BaseData):
    def __init__(self, width = 3280, height = 2494, shotTime = datetime.now()):
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
        

class PhotoData(BaseData):
    '''
    타임스탬프 값
    '''
    def __init__(self, shotTime:float = datetime.now().timestamp(), photo:bytearray = b''):
        self.id = id
        self.shotTime = shotTime
        self.photo = photo
        
    def setShotTime(self, shotTime : float):
        self.shotTime = shotTime
        
    def getShotTime(self) -> float:
        return self.shotTime
    def setPhoto(self, photo: bytearray):
        self.photo = photo
    
    def getPhoto(self) -> bytearray:
        return self.photo
    
    def toJson(self) -> str:
        return dumps({
            "shotTime" : self.shotTime,
            "photo" : b64encode(self.photo)
        })
    
    def savePhoto(self, path: str, filename: str) -> bool:
        try:
            if not os.path.isdir(path) :
                os.mkdir(path)
            file = open(os.path.join(path, filename), 'wb')
            file.write(self.photo)
            file.close()
            return True
        except Exception as e:
            print("[ERROR] " + e)
            return False
        
    def loadJson(self, txt: str):
        data = loads(txt)
        self.shotTime = data["shotTime"]
        self.photo = b64decode(data["photo"])
        
class StatusData(BaseData):
    def __init__(self, diff = 0, status = CameraStatus.DISCONNECTED):
        self.diff = diff
        self.status = status
        
    def toJson(self) -> str:
        return dumps({
            "diff" : self.diff,
            "status" : self.status.name
        })
        
    def loadJson(self, txt):
        data = loads(txt)
        self.diff = data["diff"]
        self.status = CameraStatus[data["status"]]