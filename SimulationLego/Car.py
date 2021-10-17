#--------------------------------------------------------Import libraries
import numpy as np
from pyrep import PyRep, objects
import os, sys


#--------------------------------------------------------Setup configuration
ci_build_and_not_headless = False
try:
    from cv2.version import ci_build, headless
    ci_and_not_headless = ci_build and not headless
except:
    pass
if sys.platform.startswith("linux") and ci_and_not_headless:
    os.environ.pop("QT_QPA_PLATFORM_PLUGIN_PATH")
    os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = "/home/gal/coppelia/CoppeliaSim_Edu_V4_2_0_Ubuntu20_04"
if sys.platform.startswith("linux") and ci_and_not_headless:
    os.environ.pop("QT_QPA_FONTDIR")


#--------------------------------------------------------Create Class to connect to Coppeliasim
class Car():

    # Create a class that Pyrep can communicate with Coppeliasim using the car_2.ttt
    # initialize Pyrep

    def __init__(self, pathToScene = 'LegoCar_Brown_Floor.ttt'):
        """
        Initialize the parameters to start the simulation
        :param pathToScene: path the coppeliasim environment
        """

        # Start the simulator
        SCENE_FILE = pathToScene
        self.pr    = PyRep()
        self.pr.launch(SCENE_FILE, headless = False)
        self.pr.start()

        # Set the car shape
        self.car = objects.shape.Shape("car")

        # establish steering connection
        self.front_right_steer = objects.joint.Joint("front_right_steer")
        self.rear_right_steer  = objects.joint.Joint("rear_right_steer")
        self.front_left_steer  = objects.joint.Joint("front_left_steer")
        self.rear_left_steer   = objects.joint.Joint("rear_left_steer")

        # establish motor connection
        self.front_right_motor = objects.joint.Joint("front_right_motor")
        self.rear_right_motor  = objects.joint.Joint("rear_right_motor")
        self.front_left_motor  = objects.joint.Joint("front_left_motor")
        self.rear_left_motor   = objects.joint.Joint("rear_left_motor")

        # establish steering position for rear wheels
        self.rear_right_steer.set_joint_target_velocity(0)
        self.rear_left_steer.set_joint_target_velocity(0)

        # Fix motor speed at a constant
        self.front_right_motor.set_joint_target_velocity(1)
        self.rear_right_motor.set_joint_target_velocity(1)
        self.front_left_motor.set_joint_target_velocity(1)
        self.rear_left_motor.set_joint_target_velocity(1)

        # Set Camera connection
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

        # Turn Left
        if action == 0:
            self.front_left_steer.set_joint_target_position(turningAngle)
            self.front_right_steer.set_joint_target_position(turningAngle)

        # Turn Right
        elif action == 1:
            self.front_left_steer.set_joint_target_position(-turningAngle)
            self.front_right_steer.set_joint_target_position(-turningAngle)

        # No Steering
        elif action == 2:
            self.front_left_steer.set_joint_target_position(0)
            self.front_right_steer.set_joint_target_position(0)

        # We got a problem
        else:
            raise ValueError("Too Many actions")

    def middleCheck(self,image):

        """
        :param image: takes in an image to see if line is in middle of the car for better reward
        """

        # Focus on smaller slice of image
        image = image[-40:230]


        # Get the left and right boundaries of the car's hood
        left  = image[:, 64+55, :]
        right = image[:, 192-55, :]

        # Check if there is any blue
        left_check_blue = ((left[:, 0] <= 10) & (left[:, 1] <= 10) & (200 <= left[:, 2])).sum()
        right_check_blue = ((right[:, 0] <= 10) & (right[:, 1] <= 10) & (200 <= right[:, 2])).sum()

        if (left_check_blue + right_check_blue) != 0:
            return True
        return False


    def terminalCheck(self,image):

        """
        :param image: takes in an image to see if terminal state is reached.
        Terminal state is defined if blue lane is outside of image
        """

        # focus on smaller slice of image
        image = image[-35:,:,:]

        # Get the left and right boundaries of the car's hood
        left = image[:, 64-10, :]
        right = image[:, 192-10, :]

        # check if there is any blue
        left_check_blue = ((left[:, 0] <= 10) & (left[:, 1] <= 10) & (200 <= left[:, 2])).sum()
        right_check_blue = ((right[:, 0] <= 10) & (right[:, 1] <= 10) & (200 <= right[:, 2])).sum()

        # check if there is any Green
        check_green = ((image[:, :, 0] <= 10) & (200 <= image[:, :, 1]) & (image[:, :, 2] <= 10)).sum()

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