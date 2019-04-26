import json
from BaseData import BaseData
from CameraStatus import CameraStatus

class SyncData(BaseData):
    def __init__(self, diff = 0, status = CameraStatus.DISCONNECTED):
        self.diff = diff
        self.status = status
        
    def toJson(self) -> str:
        return json.dumps({
            "diff" : self.diff,
            "status" : self.status
        })
        
    def loadJson(self, txt):
        data = json.loads(txt)
        self.diff = data["diff"]
        self.status = data["status"]