#--------------------------------------------------------Libraries
from stable_baselines import PPO2
import imageio
import numpy as np
import brickpi3
import picamera
import cv2
from functions import imageTransformationLego


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

    def terminalCheck(self,test):
        """
        :param test: takes in an image to see if terminal state is reached.
        Terminal state is defined if blue lane is outside of image
        """

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

        if (left_check_blue + right_check_blue) != 0 or (check_green) != 0:
            self.update(action=2, drive=0)
            return True
        return False


#--------------------------------------------------------Read model
model = PPO2.load("lego_model_transformed_final.zip")


#--------------------------------------------------------Start camera
images  = []
LegoCar = Car()

with picamera.PiCamera() as camera:
    with picamera.array.PiRGBArray(camera) as output:

        camera.resolution = (256, 256)
        for foo in camera.capture_continuous(output, 'rgb',use_video_port = True):

            obs       = imageTransformationLego(output.array)
            images.append(obs)
            if LegoCar.terminalCheck(obs):
                break

            action, _ = model.predict(obs, deterministic=True)

            LegoCar.update(action)
            output.truncate(0)


imageio.mimsave('foundation_lego.gif', [np.array(img) for i, img in enumerate(images) if i%2 == 0], fps=29)