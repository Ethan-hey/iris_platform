from __future__ import division

from django.shortcuts import render
from upload_app.forms import UserForm, DocumentForm

from upload_app.models import Document
import cv2
import numpy as np
import uuid, os

# Extra Imports for the Login and Logout Capabilities
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required

def index(request):
	return render(request, 'upload_app/index.html')


def intro(request):
	return render(request, 'upload_app/intro.html')


@login_required
def special(request):
    # Remember to also set login url in settings.py!
    return HttpResponse("You are logged in. Nice!")


@login_required
def user_logout(request):
    # Log out the user.
    logout(request)
    # Return to homepage.
    return render(request, 'upload_app/logout.html')


@login_required
def upload(request):
    print request.user
    if request.method == 'POST':
        username = request.user
        form = DocumentForm(request.POST, request.FILES, username)
        if form.is_valid():
            form.save()
            uploaded_file = request.FILES['document']
            # path = request.FILES['document'].upload_to
            # print 'check if image name match', filename
            
            print '-------------------------------------------------------------'
            print 'uploaded path', os.path.abspath(uploaded_file.name)
            print 'type:', type(os.path.abspath(uploaded_file.name))

            image = cv2.imread(str(os.path.abspath(uploaded_file.name)))

            # print 'type of image', type(image)
            
            return HttpResponseRedirect(request, 'index')
    else:
        form = DocumentForm()
    return render(request, 'upload_app/uploadPage.html', {'form':form})


def register(request):

    registered = False

    if request.method == 'POST':

        # Get info from "both" forms
        # It appears as one form to the user on the .html page
        user_form = UserForm(data=request.POST)

        # Check to see both forms are valid
        if user_form.is_valid():

            # Save User Form to Database
            user = user_form.save()

            # Hash the password
            user.set_password(user.password)

            # Update with Hashed password
            user.save()

            # Registration Successful!
            registered = True

        else:
            # One of the forms was invalid if this else gets called.
            print(user_form.errors)

    else:
        # Was not an HTTP post so we just render the forms as blank.
        user_form = UserForm()

    # This is the render and context dictionary to feed
    # back to the registration.html file page.
    return render(request,'upload_app/registration.html',
                          {'user_form':user_form,
                           'registered':registered})


def user_login(request):

    if request.method == 'POST':
        # First get the username and password supplied
        username = request.POST.get('username')
        password = request.POST.get('password')

        print 'username', username
        print 'password', password

        # Django's built-in authentication function:
        user = authenticate(username=username, password=password)

        # If we have a user
        if user:
            #Check it the account is active
            if user.is_active:
                # Log the user in.
                login(request,user)
                # Send the user back to some page.
                # In this case their homepage.
                return HttpResponseRedirect(reverse('index'))
            else:
                # If account is not active:
                return HttpResponse("Your account is not active.")
        else:
            print("Someone tried to login and failed.")
            print("They used username: {} and password: {}".format(username,password))
            return HttpResponse("Invalid login details supplied.")

    else:
        #Nothing has been provided for username or password.
        return render(request, 'upload_app/login.html', {})



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
    
    # x, y, r for the inner circle and outer circle
    X_in_cen, Y_in_cen, r_in = circle_in[1], circle_in[0], circle_in[2]
    X_out_cen, Y_out_cen, r_out = circle_out[1], circle_out[0], circle_out[2]
    
    thetas = np.arange(0, 2  * np.pi, 2  * np.pi / width) #Theta values
    
    # Create empty flatten image
    flat = np.zeros((height, width, 3), np.uint8)
    
    for i in range(width):
        for j in range(height):
            
            theta = thetas[i] # value of theta coordinate
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