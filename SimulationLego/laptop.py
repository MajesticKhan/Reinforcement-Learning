#--------------------------------------------------------Import libraries
import pickle
import socket
import struct
import cv2
from stable_baselines import PPO2
import numpy as np
import imageio
from functions import imageTransformationLego, terminalCheck
from PIL import Image
import time


#--------------------------------------------------------Establiosh connection
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.connect(("raspberry pi hostname",1235))


#--------------------------------------------------------Read model
model = PPO2.load("model_final.zip")


#--------------------------------------------------------Establish initial varibles
data   = bytearray()
info   = s.recv(4)
length = struct.unpack(">L", info[:4])[0]


#--------------------------------------------------------Start process
images_O  = []
images_T  = []
cv2.namedWindow('frame')
cv2.resizeWindow('frame', 256,256)
while True:

    while len(data) < length:
        data.extend(s.recv(8192))

    frame = cv2.cvtColor(cv2.imdecode(np.frombuffer(data[:length],dtype=np.uint8),1),cv2.COLOR_BGR2RGB)
    input = imageTransformationLego(frame)
    images_O.append(frame)
    images_T.append(input)
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
s.close()
imageio.mimsave('foundation_Original.gif', [np.array(img) for i, img in enumerate(images_O) if i % 2 == 0], fps=20)
imageio.mimsave('foundation_Transformed.gif', [np.array(img) for i, img in enumerate(images_T) if i % 2 == 0], fps=20)