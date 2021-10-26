#--------------------------------------------------------Import libraries
import pickle
import socket
import struct
import cv2
from stable_baselines import PPO2
import numpy as np
import imageio

#--------------------------------------------------------Establiosh connection
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.connect(("RASPBERRY PI address",1235))

#--------------------------------------------------------Read model
model = PPO2.load("model_output/model_final.zip")

#--------------------------------------------------------Establish initial varibles to hold information
data   = bytearray()
info   = s.recv(4)
length = struct.unpack(">L", info[:4])[0]

#--------------------------------------------------------Initialize
# initializes arrays to hold images for GIF
images_O  = []
cv2.namedWindow('frame')
cv2.resizeWindow('frame', 256,256)

try:
    while True:

        # Capture the bytes being sent
        while len(data) < length:
            data.extend(s.recv(4096))

        # Convert to BGR TO RGB
        frame = cv2.cvtColor(cv2.imdecode(np.frombuffer(data[:length],dtype=np.uint8),1),cv2.COLOR_BGR2RGB)

        # add raw and transformed images
        images_O.append(frame)

        # Given state, predict action
        action, _ = model.predict(frame, deterministic=True)

        # send action
        s.sendall(pickle.dumps(action))

        # Set up to get new image
        data  = data[length:]
        data.extend(s.recv(4))
        length = struct.unpack(">L", data[:4])[0]
        data   = data[4:]

        # Show image on display
        # Convert transformed image to BGR so CV2 can show image correctly
        cv2.imshow('frame',cv2.cvtColor(frame,cv2.COLOR_RGB2BGR))
        if cv2.waitKey(1) & 0xFF == ord('q'):
            s.close()
            break
finally:
    s.close()
    # convert untransformed images to gif
    imageio.mimsave('Lego_camera_view.gif', [np.array(img) for i, img in enumerate(images_O) if i % 2 == 0], fps=20)