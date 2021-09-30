#--------------------------------------------------------Import libraries
import pickle
import socket
import struct
import cv2
from stable_baselines import PPO2
import numpy as np
import imageio
from functions import imageTransformationLego, terminalCheck


#--------------------------------------------------------Establiosh connection
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.connect(("PI IP Address",1235))


#--------------------------------------------------------Read model
model = PPO2.load("model_final.zip")


#--------------------------------------------------------Establish initial varibles to hold information
data   = bytearray()
info   = s.recv(4)
length = struct.unpack(">L", info[:4])[0]


#--------------------------------------------------------Initialize
# initializes arrays to hold images for GIF
images_O  = []
images_T  = []
cv2.namedWindow('frame')
cv2.resizeWindow('frame', 256,256)


while True:

    # Capture the bytes being sent
    while len(data) < length:
        data.extend(s.recv(4096))

    # Convert to BGR TO RGB
    frame = cv2.cvtColor(cv2.imdecode(np.frombuffer(data[:length],dtype=np.uint8),1),cv2.COLOR_BGR2RGB)

    # transforms raw image to simplified image
    input = imageTransformationLego(frame)

    # add raw and transformed images
    images_O.append(frame)
    images_T.append(input)

    # check if the image creates a terminal state, if so send a signal to shutdown robot
    if terminalCheck(input):
        s.sendall(pickle.dumps(-1))
        break

    # Given state, predict action
    action, _ = model.predict(input, deterministic=True)

    # send action
    s.sendall(pickle.dumps(action))

    # Set up to get new image
    data  = data[length:]
    data.extend(s.recv(4))
    length = struct.unpack(">L", data[:4])[0]
    data   = data[4:]

    # Show image on display
    # Convert transformed image to BGR so CV2 can show image correctly
    cv2.imshow('frame',cv2.cvtColor(input,cv2.COLOR_RGB2BGR))
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# convert untransformed images to gif
imageio.mimsave('Lego_raw.gif', [np.array(img) for i, img in enumerate(images_O) if i % 2 == 0], fps=20)

# convert transformed images to gif
imageio.mimsave('Lego_transformed.gif', [np.array(img) for i, img in enumerate(images_T) if i % 2 == 0], fps=20)