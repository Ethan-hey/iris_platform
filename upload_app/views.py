from __future__ import division

from django.shortcuts import render
from upload_app.forms import UserForm, DocumentForm, DocumentFaceForm

from upload_app.models import Document, Document_face
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


# @login_required
def special(request):
    if not request.user.is_authenticated():
        return render(request, 'upload_app/require_login.html')
        # return render(request, 'upload_app/logged_in_page.html')
    # Remember to also set login url in settings.py!
    return HttpResponse("You are logged in. Nice!")


@login_required
def user_logout(request):
    # Log out the user.
    logout(request)
    # Return to homepage.
    return render(request, 'upload_app/logout.html')

def iris_gallery(request):

    if not request.user.is_authenticated():
        return render(request, 'upload_app/require_login.html')

    username = str(request.user)

    try:
        filename = Document.objects.get(username=str(request.user)).document.name
        filename = str(filename).split('/')[-1]

        path = '/media/iris/user_' + username + "/"
        iris_ori = path + filename
        iris_flat = path + 'flat_' + filename
    except:
        iris_ori = None
        iris_flat = None

    return render(request, 'upload_app/iris_gallery.html',
                 {'iris_ori':iris_ori, 'iris_flat':iris_flat})

def upload_face(request):
    if not request.user.is_authenticated():
        return render(request, 'upload_app/require_login.html')

    # Get current user's username
    username = request.user

    # Redirect if already uploaded
    query_set = DocumentFaceForm.objects.filter(username=username)
    if len(query_set) > 0:
        return render(request, 'upload_app/already_upload.html')

    if request.method == 'POST':

        # Check if inputed username matches logged username
        input_username = request.POST['username']

        # Redirect if already uploaded
        query_set = Document.objects.filter(username=username)
        if len(query_set) > 0:
            return render(request, 'upload_app/already_upload.html')

        # Redirect if not match
        print 'check if username matches', str(username) != str(input_username)
        if str(username) != str(input_username):
            return render(request, 'upload_app/fail_upload.html')

        form = DocumentFaceForm(request.POST, request.FILES, username)

        print 'check if form is valid', form.is_valid()

        if form.is_valid():
            form.save()
            uploaded_file = request.FILES['document']
            filename = request.FILES['document'].name
            suffix = str(filename).split('.')[-1]
            if not suffix in ['jpg', 'jpeg', 'png']:
                return HttpResponse("file format not supported")
            print 'suffix for current file is:', suffix

            return render(request, 'upload_app/success_upload.html')
            # return HttpResponseRedirect(request, 'index')
    else:
        form = DocumentForm()
    return render(request, 'upload_app/uploadPage.html', {'form':form})


# @login_required
def upload(request):

    if not request.user.is_authenticated():
        return render(request, 'upload_app/require_login.html')

    # Get current user's username
    username = request.user

    # Redirect if already uploaded
    query_set = Document.objects.filter(username=username)
    if len(query_set) > 0:
        return render(request, 'upload_app/already_upload.html')

    if request.method == 'POST':

        # Check if inputed username matches logged username
        input_username = request.POST['username']

        # Redirect if already uploaded
        query_set = Document.objects.filter(username=username)
        if len(query_set) > 0:
            return render(request, 'upload_app/already_upload.html')

        # Redirect if not match
        print 'check if username matches', str(username) != str(input_username)
        if str(username) != str(input_username):
            return render(request, 'upload_app/fail_upload.html')

        form = DocumentForm(request.POST, request.FILES, username)

        print 'check if form is valid', form.is_valid()

        if form.is_valid():
            form.save()
            uploaded_file = request.FILES['document']
            filename = request.FILES['document'].name
            suffix = str(filename).split('.')[-1]
            if not suffix in ['jpg', 'jpeg', 'png']:
                return HttpResponse("file format not supported")
            print 'suffix for current file is:', suffix

            path = str(os.getcwd()) + '/media/iris/user_' + str(username) + '/'
            img = cv2.imread(path + str(filename))
            flat = pre_process(img)
            cv2.imwrite(path + 'flat_' + filename, flat)

            return render(request, 'upload_app/success_upload.html')
            # return HttpResponseRedirect(request, 'index')
    else:
        form = DocumentForm()
    return render(request, 'upload_app/uploadPage.html', {'form':form})


def register(request):

    if request.user.is_authenticated():
        return render(request, 'upload_app/logged_in_page.html')

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
    circle_in = cv2.HoughCircles(image=gray,method=cv2.HOUGH_GRADIENT,dp=1,
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

            color = image[int(Xc)][int(Yc)] # color of the pixel

            flat[j][i] = color # fill color
        
    return flat