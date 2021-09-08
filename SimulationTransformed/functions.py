import numpy as np


def imageTransformation(image):

    newImage = np.zeros(image.shape)

    # fill in blue
    newImage[np.where((image[:,:,0] <= 50)    &
                      (image[:,:,0] >= 0)     &
                      (image[:, :, 1] <= 50)  &
                      (image[:, :, 1] >= 0)   &
                      (image[:, :, 2] <= 255) &
                      (image[:, :, 2] >= 180))] = [0,0,200]

    # fill in green
    newImage[np.where((image[:,:,0] <= 50)    &
                      (image[:,:,0] >= 0)     &
                      (image[:, :, 1] <= 255)  &
                      (image[:, :, 1] >= 200)   &
                      (image[:, :, 2] <= 50) &
                      (image[:, :, 2] >= 0))] = [0,200,0]
    # fill in gray
    newImage[-30:,55:199,:] =[177,176,207]

    return newImage





