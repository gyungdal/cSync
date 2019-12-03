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
    NTP = enum.auto()
    
class ParserType(enum.Enum):
    NONE = enum.auto()
    SERVER = enum.auto()
    CLIENT = enum.auto()

class CommandType(enum.Enum):
    NONE = enum.auto()
    UPDATE  = enum.auto()
    UPDATE_ZIP = enum.auto()
    VERSION = enum.auto()
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
    def __init__(self, data, sendTo : ParserType = ParserType.CLIENT):
        self.service = ServiceType.NONE
        self.command = CommandType.NONE
        self.sendTo = sendTo
        self.data = None

    def toPickle(self) -> bytes:
        return compress(dumps(
            {
                "service" : self.service,
                "command" : self.command,
                "sendTo" : self.sendTo,
                "data" : self.data
            }
        ), compresslevel=9)

    def loadPickle(self, values : bytearray):
        temp = loads(decompress(values))
        self.service = ServiceType[temp["service"]]
        self.command = CommandType[temp["command"]]
        self.sendTo = ParserType[temp["sendTo"]]
        TABLE = {
            # 클라이언트 측에서 받는 패킷
            ParserType.CLIENT : {
                ServiceType.CSYNC : {
                    CommandType.UPDATE : UpdatePacket,
                    CommandType.UPDATE_ZIP : UpdateZIPPacket,
                    CommandType.START : StartPacket
                }
            }
        }
        if self.type in TABLE[self.sendTo][self.service].keys():
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