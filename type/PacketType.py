import enum
import enum

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