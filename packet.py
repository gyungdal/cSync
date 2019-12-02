import enum
import os
import logging

from pickle import dumps, loads
from datetime import datetime
from gzip import compress, decompress
from hashlib import md5

class ServiceType(enum.Enum):
    NONE = enum.auto()
    CSYNC = enum.auto()
    CAMERA = enum.auto()
    
class CommandType(enum.Enum):
    NONE = enum.auto()
    UPDATE  = enum.auto()
    UPDATE_ZIP = enum.auto()
    START = enum.auto()
    STOP = enum.auto()
    KILL = enum.auto()
    PREPARE = enum.auto()
    STATUS = enum.auto()
    CAPTURE = enum.auto()

class BaseData:
    def toPickle(self) -> str:
        pass

    def loadPickle(self, values):
        pass

class Packet(BaseData):
    def __init__(self, data):
        self.service = ServiceType.NONE
        self.command = CommandType.NONE
        self.data = None

    def toPickle(self) -> bytes:
        return compress(dumps(
            {
                "service" : self.service,
                "command" : self.command,
                "data" : self.data
            }
        ), compresslevel=9)

    def loadPickle(self, values : bytes):
        temp = loads(decompress(values))
        self.service = ServiceType[temp["service"]]
        self.command = CommandType[temp["command"]]
        TABLE = {
            ServiceType.CSYNC : {
                CommandType.UPDATE : UpdatePacket
            }
        }
        if self.type in TABLE.keys():
            self.data = TABLE[self.type]()
            self.data.loadPickle(temp["data"])
        else:
            logging.error("not found data type")
        

# Main Process
class UpdatePacket:
    def __init__(self):
        super().__init__()
        self.version = ""
        self.url = ""

    def loadPickle(self, values):
        self.version = values["version"]
        self.url = values["url"]

class UpdateZIPPacket(BaseData):
    def __init__(self):
        super().__init__()
        self.version = ""
        self.hash = ""
        self.file = bytearray()

    def loadPickle(self, values):
        self.version = values["version"]
        self.file = values["file"]
        self.hash = values["hash"]
        with md5() as m:
            m.update(self.file)
            if m.hexdigest() != self.hash:
                logging.error("File Hash Mismatch")

class StartPacket(BaseData):
    def __init__(self):
        super().__init__()
        self.ip = ""
        self.port = 0

    def loadPickle(self, values):
        self.ip = values["ip"]
        self.port = values["port"]

class VersionResponsePacket(BaseData):
    def __init__(self):
        super().__init__()
        self.version = ""

    def loadPickle(self, values):
        self.version = values["version"]

# Sub Process
class StatusRequestPacket(BaseData):
    def __init__(self):
        super().__init__()
        self.width = 1234
        self.height = 12340
        self.awb_mode = ""
        self.exposure_mode = ""
        self.image_effect = ""
        self.brightness = 10

    def loadPickle(self, values):
        self.width = values["width"]
        self.height = values["height"]
        self.awb_mode = values["awb_mode"]
        self.exposure_mode = values["exposure_mode"]
        self.image_effect = values["image_effect"]
        self.brightness = values["brightness"]

class StatusResponse(BaseData):
    def __init__(self):
        super().__init__()
        self.ip = "0.0.0.0"
        self.useable = False
        self.width = 0
        self.height = 0
        self.awb_mode = ""
        self.exposure_mode = ""
        self.image_effect = ""
        self.brightness = 0
        self.time_offset = 0
        
    def loadPickle(self, values):
        self.ip = values["ip"]
        self.useable = values["useable"]
        self.width = values["width"]
        self.height = values["height"]
        self.awb_mode = values["awb_mode"]
        self.exposure_mode = values["exposure_mode"]
        self.image_effect = values["image_effect"]
        self.brightness = values["brightness"]
        self.time_offset = values["time_offset"]

class CaptureReuest(BaseData):
    def __init__(self):
        super().__init__()
        self.timestamp = 0
        self.light = False
    
    def loadPickle(self, values):
        self.ip = values["ip"]
        self.light = values["light"]

class CaptureResponse(BaseData):
    def __init__(self):
        super().__init__()
        self.ip = "0.0.0.0"
        self.timestamp = 0
        self.md5 = ""
        self.photo = bytearray()

    def loadPickle(self, values):
        self.ip = values["ip"]
        self.timestamp = values["timestamp"]
        self.photo = values["photo"]
        self.md5 = values["md5"]
        with md5() as m:
            m.update(self.photo)
            if m.hexdigest() != self.hash:
                logging.error("File Hash Mismatch")
                
    def savePhoto(self, dir, name)-> bool:
        try:
            if not os.path.isdir(dir) :
                os.mkdir(dir)
            file = open(os.path.join(dir, name + ".png"), 'wb')
            file.write(self.photo)
            file.close()
            return True
        except Exception as e:
            logging.error("Image Save Error " + e)
            return False
        