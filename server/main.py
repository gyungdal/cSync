from ntp_server import NTPServer
from utils import hereAmI
from file_server import fileServer
from time import sleep

fileInstance = fileServer()
ntpInstance = NTPServer()
            
def broadcast():
    hereAmI(fileServerPort=fileInstance.getPort(), ntpPort=ntpInstance.getPort())
    
if __name__ == "__main__":
    fileInstance.start()
    ntpInstance.start()
    
    broadcast()
    while True:
        try:
            value = input("CAPTURE?\nc : Capture\ns : status\nb : Broadcast\n")
            HANDLER_TABLE = {
                'c' : fileInstance.capture,
                'b' : broadcast,
                's' : fileInstance.getStatus
            }
            if value in HANDLER_TABLE.keys():
                HANDLER_TABLE[value]()
        except KeyboardInterrupt:
            print("Exiting...")
            ntpInstance.stop()
            fileInstance.stop()
            print("Exited")
            break
        