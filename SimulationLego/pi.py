#--------------------------------------------------------Import libraries
import socket
import struct
import io
import pickle
import time
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

    """
    Class used to control lego car using BrickPi3
    """

    def __init__(self):
        # Connect the motors to the ports
        self.BP            = brickpi3.BrickPi3()
        self.steering_port = self.BP.PORT_A
        self.engine_L      = self.BP.PORT_C


    def update(self,action, drive = 1):
        # Translate numeric value to steering
        if action == 0:
            direction = -1
        elif action == 1:
            direction = 1
        else:
            direction = 0
        self.BP.set_motor_position(self.steering_port,direction*90)
        self.BP.set_motor_power(self.engine_L, drive * 15)


#--------------------------------------------------------Load image

# Establish lego car connection
legoCar = Car()

try:
    # Start up camera
    with picamera.PiCamera() as camera:

        # Set up camera parameters
        camera.resolution = (256, 256)
        camera.framerate = 10

        # Start a preview and let the camera warm up for 10 seconds
        time.sleep(10)
        camera.start_preview()

        # set up stream
        frames = io.BytesIO()

        for foo in camera.capture_continuous(frames, 'jpeg',use_video_port = True):

            clientsocket.sendall(struct.pack(">L",frames.tell()) + frames.getvalue())
            frames.seek(0)
            frames.truncate()

            # receive action
            action = pickle.loads(clientsocket.recv(256))
            if action not in list(range(3)):
                legoCar.update(2,0)
                s.close()
                break
            legoCar.update(action)

finally:
    s.close()