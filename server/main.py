from ntp_server import NTPServer
from utils import Utils
from file_server import fileServer
from time import sleep

if __name__ == "__main__":
    fileInstance = fileServer()
    ntpInstance = NTPServer()
    
    fileInstance.start()
    ntpInstance.start()
    
    util = Utils()
    util.hereAmI(fileInstance.getPort(), ntpInstance.getPort())
    
    while True:
        try:
            sleep(1)
        except KeyboardInterrupt:
            print("Exiting...")
            ntpInstance.stop()
            fileInstance.stop()
            print("Exited")
            break
        