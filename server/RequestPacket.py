from pickle import dumps
VERSION = 202004.2002

class BasePacket:
    def __init__(self):
        self.version = VERSION
        self.parameter = dict()
        self.action : str = ""

    def toJson(self) -> bytes:
        return dumps({
            "version" : self.version,
            "action" : self.action,
            "parameter" : self.parameter
        })

class UpdatePacket(BasePacket):
    def __init__(self, url : str):
        BasePacket.__init__(self)
        self.action = "update"
        self.parameter["url"] = url

class SetIdPacket(BasePacket):
    def __init__(self, id):
        BasePacket.__init__(self)
        self.action = "setId"
        self.parameter["id"] = id

class GetIdPacket(BasePacket):
    def __init__(self):
        BasePacket.__init__(self)
        self.action = "getId"

class TimeSyncPacket(BasePacket):
    def __init__(self):
        BasePacket.__init__(self)
        self.action = "timesync"

class StatusPacket(BasePacket):
    def __init__(self):
        BasePacket.__init__(self)
        self.action = "status"

class SetupPacket(BasePacket):
    def __init__(self, parameter : dict):
        BasePacket.__init__(self)
        self.action = "setup"
        self.parameter = parameter.copy()

class PreparePacket(BasePacket):
    def __init__(self):
        BasePacket.__init__(self)
        self.action = "prepare"

class RestartPacket(BasePacket):
    def __init__(self):
        BasePacket.__init__(self)
        self.action = "restart"

class CapturePacket(BasePacket):
    def __init__(self, parameter : dict):
        BasePacket.__init__(self)
        self.action = "capture"
        self.parameter = parameter.copy()