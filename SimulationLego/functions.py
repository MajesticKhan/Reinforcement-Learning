#--------------------------------------------------------Import libraries
import numpy as np


#--------------------------------------------------------Create helper functions
def imageTransformationLego(image):
    """
    :param image: takes a 256x256x3 numpy array
    :return     : returns a 256x256x3 numpy array that is transformed to a simplified image
    """
    newImage = np.zeros(image.shape)

    # fill in blue
    newImage[np.where((image[:,:,0] <= 80)    &
                      (image[:,:,0] >= 0)     &
                      (image[:, :, 1] <= 140)  &
                      (image[:, :, 1] >= 0)   &
                      (image[:, :, 2] <= 255) &
                      (image[:, :, 2] >= 80))] = [0,0,200]

    # fill in green
    newImage[np.where((image[:,:,0] <= 50)    &
                      (image[:,:,0] >= 0)     &
                      (image[:, :, 1] <= 255)  &
                      (image[:, :, 1] >= 200)   &
                      (image[:, :, 2] <= 50) &
                      (image[:, :, 2] >= 0))] = [0,200,0]
    # fill in gray
    newImage[-30:,(64-10):(192+10),:] =[177,176,207]

    return newImage.astype(np.uint8)


def terminalCheck(test):
    """
    :param test: takes in an image to see if terminal state is reached.
    Terminal state is defined if blue lane is outside of image
    """

    # focus on smaller slice of image
    test = test[-35:230]


    # Get the left and right boundaries of the car's hood
    left = test[:, 64-10, :]
    right = test[:, 192+10, :]


    # check if there is any blue
    left_check_blue = ((left[:, 0] <= 10) & (left[:, 1] <= 10) & (200 <= left[:, 2])).sum()
    right_check_blue = ((right[:, 0] <= 10) & (right[:, 1] <= 10) & (200 <= right[:, 2])).sum()


    # check if there is any Green
    check_green = ((test[:, :, 0] <= 10) & (200 <= test[:, :, 1]) & (test[:, :, 2] <= 10)).sum()

    if (left_check_blue + right_check_blue) != 0 or (check_green) != 0:
        return True
    return False