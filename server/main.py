from ntp_server import NTPServer
from utils import hereAmI
from file_server import fileServer
from time import sleep

fileInstance = fileServer()
ntpInstance = NTPServer()
FLAG = True

def stop():
    global FLAG
    FLAG = False            
    
def broadcast():
    hereAmI(fileServerPort=fileInstance.getPort(), ntpPort=ntpInstance.getPort())

if __name__ == "__main__":
    fileInstance.start()
    ntpInstance.start()
    
    try:
        while FLAG:
            value = input("CAPTURE?\nc : Capture\ns : status\nb : Broadcast\ne : stop\n")
            HANDLER_TABLE = {
                'c' : fileInstance.capture,
                'b' : broadcast,
                's' : fileInstance.getStatus,
                'e' : stop
            }
            if value in HANDLER_TABLE.keys():
                HANDLER_TABLE[value]()
    except KeyboardInterrupt:
        FLAG = False
    finally:
        ntpInstance.stop()
        fileInstance.stop()
        print("Exited")
        