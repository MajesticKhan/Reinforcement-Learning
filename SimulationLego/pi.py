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
s.bind(("0.0.0.0",1235))
print("Server has been established under the hostname {}".format("0.0.0.0"))
print("Awaiting for further connection")
s.listen(1)
clientsocket, address = s.accept()


#--------------------------------------------------------class for lego car
class Car():
    def __init__(self):
        # car can go up, down, left, or right
        self.BP            = brickpi3.BrickPi3()
        self.steering_port = self.BP.PORT_A
        self.engine_L      = self.BP.PORT_C
    def update(self,action, drive = 1):
        if action == 0:
            direction = -1
        elif action == 1:
            direction = 1
        else:
            direction = 0
        self.BP.set_motor_position(self.steering_port,direction*70)
        self.BP.set_motor_power(self.engine_L, drive * 15)


#--------------------------------------------------------Load image

legoCar = Car()
with picamera.PiCamera() as camera:
    camera.resolution = (256, 256)
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
        tt = clientsocket.recv(128)
        action = pickle.loads(tt)
        if action not in list(range(3)):
            print(action)
            legoCar.update(2,0)
            s.close()
            break
        legoCar.update(action)
        print(action)