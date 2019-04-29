from ntp_server import NTPServer
from utils import hereAmI
from file_server import fileServer
from time import sleep

            
if __name__ == "__main__":
    fileInstance = fileServer()
    ntpInstance = NTPServer()
    
    fileInstance.start()
    ntpInstance.start()
    
    hereAmI(fileServerPort=fileInstance.getPort(), ntpPort=ntpInstance.getPort())
    
    while True:
        try:
            value = input("CAPTURE?\ny : Capture\ns : status")
            if value == 'y' :
                fileInstance.capture()
            elif value == 's' :
                fileInstance.getStatus()
        except KeyboardInterrupt:
            print("Exiting...")
            ntpInstance.stop()
            fileInstance.stop()
            print("Exited")
            break
        