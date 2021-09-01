import time
from multiprocessing import Process

PROCESSES = 10

import gym
import numpy as np
from gym.utils import seeding
from pyrep import PyRep, objects
from gym import spaces
from stable_baselines import PPO2
import os, sys
from stable_baselines.common.policies import CnnPolicy
from stable_baselines.common.callbacks import BaseCallback
from stable_baselines.common.evaluation import evaluate_policy
from multiprocessing import Process, Queue
from multiprocessing import Manager
from stable_baselines.common.callbacks import EvalCallback, StopTrainingOnRewardThreshold


ci_build_and_not_headless = False
try:
    from cv2.version import ci_build, headless
    ci_and_not_headless = ci_build and not headless
except:
    pass
if sys.platform.startswith("linux") and ci_and_not_headless:
    os.environ.pop("QT_QPA_PLATFORM_PLUGIN_PATH")
    os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = "/home/gal/coppelia/CoppeliaSim_Edu_V4_2_0_Ubuntu18_04"
if sys.platform.startswith("linux") and ci_and_not_headless:
    os.environ.pop("QT_QPA_FONTDIR")

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

    def terminalCheck(self,test):

        # focus on smaller slice of image
        test = test[-40:230]

        # Get the left and right boundaries of the car's hood
        left = test[:, 55, :]
        right = test[:, 198, :]

        # check if there is any blue
        left_check_blue = ((left[:, 0] <= 10) & (left[:, 1] <= 10) & (200 <= left[:, 2])).sum()
        right_check_blue = ((right[:, 0] <= 10) & (right[:, 1] <= 10) & (200 <= right[:, 2])).sum()

        # check if there is any Green
        check_green = ((test[:, :, 0] <= 10) & (200 <= test[:, :, 1]) & (test[:, :, 2] <= 10)).sum()

        if (left_check_blue + right_check_blue) != 0:
            return "Blue"

        if (check_green) != 0:
            return "Green"

        return None

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

def run():
  pr = Car()
  print("start")
  time.sleep(20)
  print("end")
  pr.shutdown()

processes = [Process(target=run, args=()) for i in range(2)]
[p.start() for p in processes]
[p.join() for p in processes]