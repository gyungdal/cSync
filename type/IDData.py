import json

from BaseData import BaseData
 
class IDData(BaseData):
    def __init__(self, id = 0):
        self.id = id
        
    def toJson(self) -> str:
        return json.dumps({
            "id" : id
        })
        
    def loadJson(self, txt):
        self.id = json.loads(txt)["id"]