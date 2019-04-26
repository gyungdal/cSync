import base64
import json
from BaseData import BaseData

class PhotoData(BaseData):
    def __init__(self, photo):
        self.id = id
        self.photo = photo
        
    def toJson(self) -> str:
        return json.dumps({
            "photo" : base64.b64encode(self.photo)
        })
        
    def loadJson(self, txt):
        data = json.loads(txt)
        self.photo = data["photo"]