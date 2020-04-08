import logging
from json import loads, dumps

logging.basicConfig(level=logging.DEBUG)

class ResponseHandler:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    # 여기서 부터는 받아 올때 쓰는 핸들러들
    async def capture(self, id : str, packet : dict): 
        from os import path, mkdir
        from base64 import b64decode
        current_path = path.dirname(path.abspath(__file__))
        self.logger.info("[%s] capture : %f\t format : %s" % (id, float(packet["parameter"]["time"]), packet["parameter"]["format"]))
        file_name = "%s.%s" % (id, packet["parameter"]["format"])
        full_path = path.join(current_path,  packet["parameter"]["time"], file_name)
        dir_path = path.dirname(full_path)
        if not path.exists(dir_path) and not path.isdir(dir_path):
            mkdir(dir_path)
        with open(full_path, "w+") as f:
            f.write(b64decode(packet["parameter"]["data"].decode("utf-8")))

    async def timesync(self, id : str, packet : dict): 
        self.logger.info("[%s] timesync : %f" % (id, float(packet["parameter"]["timediff"])))

    async def getId(self, id : str, packet : dict): 
        self.logger.info("getId : %s" % packet["parameter"]["id"])
    
    async def status(self, id : str, packet : dict): 
        self.logger.debug("Status : %s" % dumps(packet["parameter"]))

    async def setup(self, id : str, packet : dict): 
        self.logger.info("Setup : %s" % dumps(packet["parameter"]))
