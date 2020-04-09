import logging
from pickle import loads, dumps

logging.basicConfig(level=logging.DEBUG)

class ResponseHandler:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    # 여기서 부터는 받아 올때 쓰는 핸들러들
    async def capture(self, id : str, packet : dict): 
        from os import path, mkdir
        from base64 import b64decode
        from datetime import datetime
        from lzma import decompress
        current_path = path.dirname(path.abspath(__file__))
        capture_time = str(datetime.utcfromtimestamp(float(packet['parameter']['time']) / 1000))
        self.logger.info(f"[{id}] capture : {capture_time }\t format : {packet['parameter']['format']}")
        file_name = f"{id}.{packet['parameter']['format']}"
        full_path = path.join(current_path, capture_time, file_name)
        dir_path = path.dirname(full_path)
        if not path.exists(dir_path) and not path.isdir(dir_path):
            mkdir(dir_path)
        with open(full_path, "wb") as f:
            f.write(decompress(packet["parameter"]["data"].encode("utf-8")))

    async def timesync(self, id : str, packet : dict): 
        self.logger.info(f"[{id}] timesync : {float(packet['parameter']['timediff'])}")

    async def getId(self, id : str, packet : dict): 
        self.logger.info(f"getId : {packet['parameter']['id']}")
    
    async def status(self, id : str, packet : dict): 
        self.logger.debug(f"Status : {dumps(packet['parameter'])}")

    async def setup(self, id : str, packet : dict): 
        self.logger.info(f"Setup : {dumps(packet['parameter'])}")
