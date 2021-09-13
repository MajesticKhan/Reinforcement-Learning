#--------------------------------------------------------Import libraries
import socket
import struct
import io
import pickle
import numpy as np
import picamera
import picamera.array
import sys
import brickpi3

#--------------------------------------------------------Establish connection
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.bind(("0.0.0.0",1234))
print("Server has been established under the hostname {}".format("0.0.0.0"))
print("Awaiting for further connection")
s.listen(1)
clientsocket, address = s.accept()


#--------------------------------------------------------Transformation
def imageTransformationLego(image):

    newImage = np.zeros(image.shape)

    # fill in blue
    newImage[np.where((image[:,:,0] <= 60)    &
                      (image[:,:,0] >= 0)     &
                      (image[:, :, 1] <= 120)  &
                      (image[:, :, 1] >= 0)   &
                      (image[:, :, 2] <= 255) &
                      (image[:, :, 2] >= 100))] = [0,0,200]

    # fill in green
    newImage[np.where((image[:,:,0] <= 50)    &
                      (image[:,:,0] >= 0)     &
                      (image[:, :, 1] <= 255)  &
                      (image[:, :, 1] >= 200)   &
                      (image[:, :, 2] <= 50) &
                      (image[:, :, 2] >= 0))] = [0,200,0]
    # fill in gray
    newImage[-30:,55:199,:] =[177,176,207]

    return newImage.astype(np.uint8)

#--------------------------------------------------------class for lego car
class Car():
    def __init__(self):
        # car can go up, down, left, or right
        self.BP            = brickpi3.BrickPi3()
        self.steering_port = self.BP.PORT_A
        self.engine_R      = self.BP.PORT_B
        self.engine_L      = self.BP.PORT_C
    def update(self,action, drive = 1):
        if action == 0:
            direction = -1
        elif action == 1:
            direction = 1
        else:
            direction = 0
        self.BP.set_motor_position(self.steering_port,direction*2500)
        self.BP.set_motor_power(self.engine_R, drive * 15)
        self.BP.set_motor_power(self.engine_L, -drive * 15)


#--------------------------------------------------------Load image

legoCar = Car()
with picamera.PiCamera() as camera:
    camera.resolution = (245, 256)
    camera.framerate = 60
    # Start a preview and let the camera warm up for 2 seconds
    camera.start_preview()
    # Note the start time and construct a stream to hold image data
    # temporarily (we could write it directly to connection but in this
    # case we want to find out the size of each capture first to keep
    # our protocol simple)
    frames = io.BytesIO()
    for foo in camera.capture_continuous(frames, 'jpeg',use_video_port = True):
        clientsocket.sendall(struct.pack(">L",frames.tell()) + frames.getvalue())
        frames.seek(0)
        frames.truncate()
        tt = clientsocket.recv(4096)
        print(len(tt))
        action = pickle.loads(tt)
        if action not in list(range(3)):
            print(action)
            legoCar.update(2,0)
            break
        legoCar.update(action)
        print(action)
