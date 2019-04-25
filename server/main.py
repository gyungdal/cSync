from ntp_server import NTPServer
from utils import Utils

if __name__ == "__main__":
    ntpInstance = NTPServer()
    ntpInstance.start()
    
    util = Utils()
    util.hereAmI(, ntpInstance.getPort())
    
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            print("Exiting...")
            ntpInstance.stop()
            print("Exited")
            break
        