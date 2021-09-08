from os.path import dirname, join, abspath
import os
import imageio
import numpy as np
from PIL import Image


from pyrep import PyRep, objects
import pygame
pygame.init()
WINDOW_WIDTH = 1
WINDOW_HEIGHT= 1
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

def blueCheckLine(test):
    test = test[-64:,:,:]
    left  = test[:,0,:]
    right = test[:,-1,:]

    # check if there is any blue
    left_check  = ((left[:,0] <= 10) & (left[:,1] <= 10) & (200 <=left[:,2])).sum()
    right_check = ((right[:,0] <= 10) & (right[:,1] <= 10) & (200 <=right[:,2])).sum()

    if (left_check + right_check) != 0:
        Image.fromarray(test).save("quit_upclose.jpeg")
        return False
    return True



class Car():

    # initialize
    def __init__(self, pathToScene = '/home/gal/coppelia/project/legocar.ttt'):
        """
        Initialize the parameters to start the simulation
        :param pathToScene:
        """
        # Start the simulator
        SCENE_FILE = pathToScene
        self.pr    = PyRep()
        self.pr.launch(SCENE_FILE, headless = False)
        self.pr.start()

        # Set the car shape
        self.car = objects.shape.Shape("car")

        # establish steering
        self.front_right_steer = objects.joint.Joint("front_right_steer")
        self.rear_right_steer  = objects.joint.Joint("rear_right_steer")
        self.front_left_steer  = objects.joint.Joint("front_left_steer")
        self.rear_left_steer   = objects.joint.Joint("rear_left_steer")

        # establish motor
        self.front_right_motor = objects.joint.Joint("front_right_motor")
        self.rear_right_motor  = objects.joint.Joint("rear_right_motor")
        self.front_left_motor  = objects.joint.Joint("front_left_motor")
        self.rear_left_motor   = objects.joint.Joint("rear_left_motor")

        # establish steering position for rear wheels TODO: motor should be disabled
        self.rear_right_steer.set_joint_target_velocity(0)
        self.rear_left_steer.set_joint_target_velocity(0)

        # Fix motor speed
        self.front_right_motor.set_joint_target_velocity(1)
        self.rear_right_motor.set_joint_target_velocity(1)
        self.front_left_motor.set_joint_target_velocity(1)
        self.rear_left_motor.set_joint_target_velocity(1)

        # Set Camera
        self.camera = objects.vision_sensor.VisionSensor("frontCamera")


    def captureImage(self):

        """
        :return: return current image based on camera feed
        """

        return np.uint8(self.camera.capture_rgb() * 255.)


    def steering(self, action, turningAngle = .2):
        """
        :param action       : either turn left or right
        :param turningAngle : angle of turning the wheel
        """

        # If action is left
        if action == 0:
            self.front_left_steer.set_joint_target_position(turningAngle)
            self.front_right_steer.set_joint_target_position(turningAngle)

        # if action is right
        elif action == 1:
            self.front_left_steer.set_joint_target_position(-turningAngle)
            self.front_right_steer.set_joint_target_position(-turningAngle)

        # if action is no steering
        elif action == 2:
            self.front_left_steer.set_joint_target_position(0)
            self.front_right_steer.set_joint_target_position(0)

        else:
            raise ValueError("Too Many actions")

    def updateSimulation(self):

        # Step through the simulation
        self.pr.step()


    def reset(self):
        """
        Return the car to the original position
        """
        self.car.set_pose([6.7750e+00,6.4750e+00,1.7500e-01,0,0, 7.08272636e-01 , 7.05938995e-01])

    def shutdown(self):

        """
        Shutdown the simulation
        """
        self.pr.stop()
        self.pr.shutdown()


car = Car()

while True:
    pygame.event.pump()

    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_RIGHT:
                car.steering(1,.2)
            elif event.key == pygame.K_LEFT:
                car.steering(0, .2)
            elif event.key == pygame.K_UP:
                car.steering(2,.2)
            elif event.key == pygame.K_DOWN:
                Image.fromarray(car.captureImage()).save("testCapture.jpeg")
                car.shutdown()
    car.updateSimulation()


#https://github.com/stepjam/PyRep/issues/142
#https://github.com/stepjam/PyRep/issues/8
#https://askubuntu.com/questions/308128/failed-to-load-platform-plugin-xcb-while-launching-qt5-app-on-linux-without