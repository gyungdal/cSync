from picamera import PiCamera
from io import BytesIO
import time
from datetime import datetime
stream = BytesIO()
camera = PiCamera()
camera.resolution = (3280, 2464)
# Camera warm-up time
time.sleep(5)

start = datetime.now().timestamp()
camera.capture(stream, 'png')
print("{} 소요".format(datetime.now().timestamp() - start))
