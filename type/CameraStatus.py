import enum

class CameraStatus(enum.Enum):
    OK = enum.auto()
    
    BUSY = enum.auto()
    DISCONNECTED = enum.auto()
    