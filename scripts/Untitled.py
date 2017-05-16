
# coding: utf-8

# In[1]:

import cv2


# In[2]:

img =cv2.imread('DSC_0604ok.jpg')


# In[3]:

cv2.namedWindow("Image")
cv2.imshow('Image', img)
cv2.waitKey(0)


# In[1]:

def create_blank_img(width, height, rgb_color=(0, 0, 0)):
    """Create new image(numpy array) filled with certain color in RGB"""
    # Create black blank image
    image = np.zeros((height, width, 3), np.uint8)

    # Since OpenCV uses BGR, convert the color first
    color = tuple(reversed(rgb_color))
    # Fill image with color
    image[:] = color

    return image


# In[ ]:



