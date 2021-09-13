
#--------------------------------------------------------Import libraries
import pickle
import socket
import struct
import numpy as np
import cv2
from stable_baselines import PPO2
import imageio
import numpy as np
import imageio

#--------------------------------------------------------Establiosh connection
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.connect(("192.168.1.5",1234))


#--------------------------------------------------------Read model
model = PPO2.load("/SimulationTransformed/lego_model_transformed_final.zip")


#--------------------------------------------------------Establish initial varibles
data   = bytearray()
info   = s.recv(4)
length = struct.unpack(">L", info[:4])[0]


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
def terminalCheck(test):
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
        return True
    return False

#--------------------------------------------------------Start process
images  = []
cv2.namedWindow('frame')
cv2.resizeWindow('frame', 256,256)
while True:

    while len(data) < length:
        data.extend(s.recv(4096))


    frame = cv2.imdecode(np.frombuffer(data[:length],dtype=np.uint8),1)
    images.append(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    imageio.mimsave('foundation_lego.gif', [np.array(img) for i, img in enumerate(images) if i % 2 == 0], fps=29)
    input = imageTransformationLego(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    if terminalCheck(input):
        s.sendall(pickle.dumps(-1))
        break
    action, _ = model.predict(input, deterministic=True)
    print(action)
    s.sendall(pickle.dumps(action))

    frame = cv2.cvtColor(input,cv2.COLOR_RGB2BGR)


    data  = data[length:]
    data.extend(s.recv(4))
    length = struct.unpack(">L", data[:4])[0]
    data   = data[4:]

    cv2.imshow('frame',frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break