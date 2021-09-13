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