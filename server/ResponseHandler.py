class ResponseHandler:
    # 여기서 부터는 받아 올때 쓰는 핸들러들
    async def capture(self, packet : dict): 
        pass

    async def timesync(self, packet : dict): 
        pass

    async def setId(self, packet : dict): 
        pass

    async def getId(self, packet : dict): 
        pass
    
    async def status(self, packet : dict): 
        pass

    async def version(self, packet : dict): 
        pass
