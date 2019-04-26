import json
import datetime

from BaseData import BaseData

class CameraSetupData(BaseData):
    def __init__(self, width = 3240, height = 2494, shotTime = datetime.datetime.now()):
        self.width = width
        self.height = height
        self.shotTime = shotTime
        
    def toJson(self) -> str:
        return json.dumps({
            "width" : self.width,
            "height" : self.height,
            "shotTime" : self.shotTime
        })
        
    def loadJson(self, txt):
        data = json.loads(txt)
        self.shotTime = data["shotTime"]
        self.width = data["width"]
        self.height = data["height"]