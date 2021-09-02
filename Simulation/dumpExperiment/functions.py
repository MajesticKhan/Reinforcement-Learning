import numpy as np
from PIL import Image

test = Image.open("quit.jpeg")
test = np.asarray(test)
test = test.copy()

tt = Image.fromarray(test[-64:,:,:])


def blueCheckLine(test):

    left  = test[:,0,:]
    right = test[:,-1,:]

    # check if there is any blue
    left_check  = ((left[:,0] <= 50) & (left[:,1] <= 50) & (150 <=left[:,2])).sum()
    right_check = ((right[:,0] <= 50) & (right[:,1] <= 50) & (150 <=right[:,2])).sum()

    if (left_check + right_check) != 0:
        return False
    return True

test[:,55,:] = np.array([255,0,0])
test[:,198,:] = np.array([255,0,0])
Image.fromarray(test[-40:230]).save("Alex.jpeg")