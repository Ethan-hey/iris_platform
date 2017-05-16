import cv2
import numpy as np
from __future__ import division


def pre_process(image, width=360, height=60):
    
    # Convert image to gray and blur
    gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 17)
    
    # Use Hough transform to detect circle
    ret, th3 = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    circle_in = cv2.HoughCircles(image=gray,method=cv2.cv.CV_HOUGH_GRADIENT,dp=1,
                            minDist=50,param1=ret,param2=30,minRadius=1,maxRadius=200)[0][0]
    circle_out = circle_in.copy()
    circle_out[2] = 120
      
    flat_img = flatten_img(image, circle_in, circle_out, width, height)

    def flatten_img(image, circle_in, circle_out, width=360, height=60):
    
	    # x, y, r for the inner circle and outer circle
	    X_in_cen, Y_in_cen, r_in = circle_in[1], circle_in[0], circle_in[2]
	    X_out_cen, Y_out_cen, r_out = circle_out[1], circle_out[0], circle_out[2]
	    
	    thetas = np.arange(0, 2  * np.pi, 2  * np.pi / width) #Theta values
	    
	    # Create empty flatten image
	    flat = np.zeros((height, width, 3), np.uint8)
	    
	    for i in range(width):
	        
	        theta = thetas[i] # value of theta coordinate
	        
	        for j in range(height):
	            
	            r_pro = j / height # value of r coordinate(normalized)

	            # get coordinate of boundaries
	            Xi = X_in_cen + r_in * np.cos(theta)
	            Yi = Y_in_cen + r_in * np.sin(theta)
	            Xo = X_out_cen + r_out * np.cos(theta)
	            Yo = Y_out_cen + r_out * np.sin(theta)

	            # the matched cartesian coordinates for the polar coordinates
	            Xc = (1 - r_pro) * Xi + r_pro * Xo
	            Yc = (1 - r_pro) * Yi + r_pro * Yo

	            color = img[int(Xc)][int(Yc)] # color of the pixel

	            flat[j][i] = color # fill color
	            
	    return flat

	def create_blank_img(width, height, rgb_color=(0, 0, 0)):
	    """Create new image(numpy array) filled with certain color in RGB"""
	    # Create black blank image
	    image = np.zeros((height, width, 3), np.uint8)

	    # Since OpenCV uses BGR, convert the color first
	    color = tuple(reversed(rgb_color))
	    # Fill image with color
	    image[:] = color

	    return image
    
    return flat_img






