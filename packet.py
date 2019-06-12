import enum
import os

from pickle import dumps, loads
from datetime import datetime
from gzip import compress, decompress

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
    def toPickle(self) -> str:
        pass

    def loadPickle(self, txt):
        pass
    
class Packet:
    def __init__(self, tp : PacketType, data):
        self.version = '20190612_dev'
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
    
    def toPickle(self) -> str:
        return dumps({
            "version": self.version,
            "data": self.data.toPickle(),
            "type": self.type.name
        })

    def loadPickle(self, Pickle):
        temp = loads(Pickle)
        self.version = temp["version"]
        self.type = PacketType[temp["type"]]
        TABLE = {
            PacketType.SET_CLIENT_ID : IDData(),
            PacketType.REQUEST_ID : None,
            PacketType.RESPONSE_ID : IDData(),
            PacketType.REQUEST_STATUS : None,
            PacketType.RESPONSE_STATUS : StatusData(),
            PacketType.REQUEST_CAPTURE : CaptureSetupData(),
            PacketType.RESPONSE_CAPTURE : PhotoData(),
            PacketType.REQUEST_EXIT : None
        }
        self.data = TABLE[self.type]
        if self.data != None:
            self.data.loadPickle(temp["data"])
        
class IDData(BaseData):
    def __init__(self, id = 0):
        self.id = id
        
    def toPickle(self) -> str:
        return dumps({
            "id" : self.id
        })
        
    def loadPickle(self, txt):
        self.id = loads(txt)["id"]
        
class CaptureSetupData(BaseData):
    def __init__(self, width = 3280, height = 2464, shotTime = datetime.now(), pt = '', name=''):
        self.width = width
        self.height = height
        self.shotTime = shotTime
        self.pt = pt
        self.name = name
        
    def toPickle(self) -> str:
        return dumps({
            "width" : self.width,
            "height" : self.height,
            "shotTime" : self.shotTime,
            "pt" : self.pt,
            "name" : self.name
        })
        
    def loadPickle(self, txt):
        data = loads(txt)
        self.shotTime = data["shotTime"]
        self.width = data["width"]
        self.height = data["height"]
        self.pt = data["pt"]
        self.name = data["name"]
        

class PhotoData(BaseData):
    '''
    타임스탬프 값
    '''
    def __init__(self, shotTime:float = datetime.now().timestamp(), 
                 photo:bytearray = b'', pt = '', name=''):
        self.id = id
        self.shotTime = shotTime
        self.photo = photo
        self.name = name
        self.pt = pt
        
    def setShotTime(self, shotTime : float):
        self.shotTime = shotTime
        
    def getShotTime(self) -> float:
        return self.shotTime
    
    def setPhoto(self, photo: bytearray):
        self.photo = photo
    
    def getPhoto(self) -> bytearray:
        return self.photo
    
    def toPickle(self) -> str:
        return dumps({
            "shotTime" : self.shotTime,
            "photo" : compress(self.photo, compresslevel=9),
            "pt" : self.pt,
            "name" : self.name
        })
    
    def loadPickle(self, txt: str):
        data = loads(txt)
        self.shotTime = data["shotTime"]
        self.photo = decompress(data["photo"])
        self.name = data['name']
        self.pt = data['pt']
        
    def savePhoto(self) -> bool:
        try:
            if not os.path.isdir(self.pt) :
                os.mkdir(self.pt)
            file = open(os.path.join(self.pt, self.name), 'wb')
            file.write(self.photo)
            file.close()
            return True
        except Exception as e:
            print("[ERROR] " + e)
            return False
        
class StatusData(BaseData):
    def __init__(self, diff = 0, status = CameraStatus.DISCONNECTED):
        self.diff = diff
        self.status = status
        
    def toPickle(self) -> str:
        return dumps({
            "diff" : self.diff,
            "status" : self.status.name
        })
        
    def loadPickle(self, txt):
        data = loads(txt)
        self.diff = data["diff"]
        self.status = CameraStatus[data["status"]]