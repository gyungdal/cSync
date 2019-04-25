from json import dumps, loads

class CameraParam:
    def __init__(self):
        self.version = '20190425_dev'
        self.shoot_time = 0
        
    def toJson(self):
        return dumps({
            "shoot_time" : self.shoot_time,
            "version" : self.version
        })
        
    def loadJson(self, json):
        temp = loads(json)
        self.version = temp["version"]
        self.shoot_time = temp["shoot_time"]