import picamera

camera = picamera.PiCamera()
camera.resolution = (2592, 1944)
camera.framerate = 15
camera.capture('image.png')
camera.close()