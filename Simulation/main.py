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

def terminalCheck(test):

    # focus on smaller slice of image
    test  = test[-40:230]

    # Get the left and right boundaries of the car's hood
    left  = test[:,55,:]
    right = test[:,198,:]

    # check if there is any blue
    left_check_blue  = ((left[:,0] <= 10) & (left[:,1] <= 10) & (200 <=left[:,2])).sum()
    right_check_blue = ((right[:,0] <= 10) & (right[:,1] <= 10) & (200 <=right[:,2])).sum()

    # check if there is any Green
    check_green  = ((test[:,:,0] <= 10) & (200 <= test[:,:,1]) & (test[:,:,2]  <= 10)).sum()

    if (left_check_blue + right_check_blue) != 0:
        Image.fromarray(test).save("quit_upclose_blue.jpeg")
        return "Blue"

    if (check_green) != 0:
        Image.fromarray(test).save("quit_upclose_green.jpeg")
        return "Green"
    return False

LOOPS = 4
SCENE_FILE = '/home/gal/coppelia/project/legocar.ttt'
pr = PyRep()
pr.launch(SCENE_FILE, headless=False)
pr.start()
car = objects.shape.Shape("car")

# establish steering
front_right_steer = objects.joint.Joint("front_right_steer")
rear_right_steer  = objects.joint.Joint("rear_right_steer")
front_left_steer  = objects.joint.Joint("front_left_steer")
rear_left_steer   = objects.joint.Joint("rear_left_steer")

# establish motor
front_right_motor = objects.joint.Joint("front_right_motor")
rear_right_motor  = objects.joint.Joint("rear_right_motor")
front_left_motor  = objects.joint.Joint("front_left_motor")
rear_left_motor   = objects.joint.Joint("rear_left_motor")

# Set turn
#front_right_steer.set_joint_target_velocity(2.5)
rear_right_steer.set_joint_target_velocity(0)
#front_left_steer.set_joint_target_velocity(2.5)
rear_left_steer.set_joint_target_velocity(0)

# Set motor
front_right_motor.set_joint_target_velocity(1)
rear_right_motor.set_joint_target_velocity(1)
front_left_motor.set_joint_target_velocity(1)
rear_left_motor.set_joint_target_velocity(1)

# set image
camera = objects.vision_sensor.VisionSensor("frontCamera")
images=[]
turningAngle =.2
counter = 0
while True:
    counter +=1
    print(counter)
    im = np.uint8(camera.capture_rgb() * 255.)

    if terminalCheck(im) in ["Blue","Green"]:
        print("----------------------------Crossed!!, terminate")
        Image.fromarray(im).save("quit.jpeg")
        pr.stop()
        pr.shutdown()

    pygame.event.pump()

    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_RIGHT:
                front_left_steer.set_joint_target_position(-turningAngle)
                front_right_steer.set_joint_target_position(-turningAngle)
            elif event.key == pygame.K_LEFT:
                front_left_steer.set_joint_target_position(turningAngle)
                front_right_steer.set_joint_target_position(turningAngle)
            elif event.key == pygame.K_UP:
                front_left_steer.set_joint_target_position(0)
                front_right_steer.set_joint_target_position(0)
            elif event.key == pygame.K_DOWN:
                Image.fromarray(im).save("quit.jpeg")
                #imageio.mimsave('test.gif', [np.array(img) for i, img in enumerate(images)], fps=29)
                car.set_position([6.7750e+00,6.4750e+00,1.7500e-01])

#                pr.stop()
#                pr.shutdown()
    pr.step()

#https://github.com/stepjam/PyRep/issues/142
#https://github.com/stepjam/PyRep/issues/8
#https://askubuntu.com/questions/308128/failed-to-load-platform-plugin-xcb-while-launching-qt5-app-on-linux-without