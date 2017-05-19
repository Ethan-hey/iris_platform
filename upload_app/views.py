from __future__ import division

from django.shortcuts import render
from upload_app.forms import UserForm, DocumentForm, DocumentFaceForm

from upload_app.models import Document, Document_face
from scipy.linalg import norm
from scipy import sum, average
from os import path
from glob import glob 
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

def face_gallery(request):

    # return HttpResponse("face_gallery")

    if not request.user.is_authenticated():
        return render(request, 'upload_app/require_login.html')

    username = str(request.user)
    print 'username trying to query here is:', str(username)
    print len(Document_face.objects.filter(username=str(username)))

    filename = Document_face.objects.get(username=str(request.user)).document.name

    try:
        filename = Document_face.objects.get(username=str(request.user)).document.name
        print 'filename = Document_face.objects.get(username=str(request.user)).document.name'
        filename = str(filename).split('/')[-1]
        print "filename = str(filename).split('/')[-1]"

        path = '/media/iris/user_' + username + "/"
        print "path = '/media/iris/user_' + use"
        face_ori = path + filename
        print 'face_ori = path + filename'
    except:
        face_ori = None

    return render(request, 'upload_app/face_gallery.html',
                 {'face_ori':face_ori})


def upload_face(request):
    if not request.user.is_authenticated():
        return render(request, 'upload_app/require_login.html')

    # Get loggedin user's username
    username = request.user

    # Redirect if already uploaded
    query_set = Document_face.objects.filter(username=username)
    if len(query_set) > 0:
        error_message = "You've already uploaded. Maximum image number allowed: one"
        return render(request, 'upload_app/fail_upload.html', {'error_message':error_message})

    if request.method == 'POST':

        # Check if inputed username matches logged username
        input_username = request.POST['username']

        # Redirect if not match
        print 'check if username matches', str(username) == str(input_username)
        if str(username) != str(input_username):
            error_message='Username mismatch'
            return render(request, 'upload_app/fail_upload.html', {'error_message':error_message})

        form = DocumentFaceForm(request.POST, request.FILES, username)

        print 'check if form is valid', form.is_valid()

        if form.is_valid():

            form.save() # save uploaded info to database

            uploaded_file = request.FILES['document']
            filename = request.FILES['document'].name

            # check file suffix
            suffix = str(filename).split('.')[-1] 
            if not suffix in ['jpg', 'jpeg', 'png']:
                error_message = 'File format not supported'
                return render(request, 'upload_app/fail_upload.html', {'error_message':error_message})
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
    username = str(request.user)

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
            error_message = "You've already uploaded. Maximum image number allowed: one"
            return render(request, 'upload_app/fail_upload.html', {'error_message':error_message})

        # Redirect if not match
        print 'check if username matches', str(username) == str(input_username)
        if str(username) != str(input_username):
            error_message = 'Username mismatchs. Please check your username and upload again.'
            return render(request, 'upload_app/fail_upload.html', {'error_message':error_message})

        form = DocumentForm(request.POST, request.FILES, username)

        print 'check if form is valid', form.is_valid()

        if form.is_valid():
            form.save()

            doc_obj = Document.objects.get(username=username)

            uploaded_file = request.FILES['document']
            filename = request.FILES['document'].name
            suffix = str(filename).split('.')[-1]
            if not suffix in ['jpg', 'jpeg', 'png']:
                doc_obj.delete()
                error_message = 'File format not supported.'
                return render(request, 'upload_app/fail_upload.html', {'error_message':error_message})
            # print 'suffix for current file is:', suffix

            path = str(os.getcwd()) + '/media/iris/user_' + str(username) + '/'
            img = cv2.imread(path + str(filename))
            if not judge_similarity(img, verbose=True):
                doc_obj.delete()
                error_message = "Your image doesn't look like an iris image"
                return render(request, 'upload_app/fail_upload.html', {'error_message':error_message})
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
                            minDist=50,param1=ret,param2=30,minRadius=10,maxRadius=100)[0][0]
    circle_out = circle_in.copy()
    circle_out[2] = 90
    
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


def normalize(arr):
    rng = arr.max()-arr.min()
    amin = arr.min()
    return (arr-amin)*255/rng

def crop_resize(img, height=480, width=640):
    
    imgH = img.shape[0]
    imgW = img.shape[1]
        
    ratio = height / width
    img_ratio = imgH / imgW
        
    # adjust height to width ratio to required size
    if img_ratio > ratio:
        c_img = img[0:int(ratio * imgW), 0:imgW]
    elif img_ratio < ratio:
        c_img = img[0:imgH, 0:int(imgH / ratio)]
    else:
        c_img = img[0:imgH, 0:imgW]
         
    c_img = cv2.resize(c_img, (height, width)) # adjust resolution
    return c_img


def compare_images(img1, img2, verbose=False):
    
    # convert image to gray scale
    img1 = cv2.cvtColor(img1,cv2.COLOR_BGR2GRAY)
    img2 = cv2.cvtColor(img2,cv2.COLOR_BGR2GRAY)
    print 'type of images after gray', type(img1), type(img2)
    print img1.shape, img2.shape
    
    # crop images to required size
    img1 = crop_resize(img1)
    img2 = crop_resize(img2)
    print 'type of images after crop and resize:', type(img1), type(img2)
    print img1.shape, img2.shape
    
    # normalize images
    img1 = normalize(img1)
    img2 = normalize(img2)
    print 'type of images after normalzie:', type(img1), type(img2)
    print img1.shape, img2.shape
    
    # calculate the difference and its norms
    diff = img1 - img2  # elementwise for scipy arrays
    m_norm = sum(abs(diff))  # Manhattan norm
    z_norm = norm(diff.ravel(), 0)  # Zero norm
    if verbose:
        print "Manhattan norm per pixel:", m_norm/img1.size
    
    return (m_norm/img1.size)



# read ten iris images as sample images
def get_samples(dr="scripts/sample_images/", ext="jpg"):
    print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
    print os.getcwd()
    print path.join(dr,"*.{}".format(ext))
    images = glob(path.join(dr,"*.{}".format(ext)))
    for i in range(len(images)):
        img = images[i]
        img = cv2.imread(img)
        images[i] = img
    return images

# check if uploaded image similar to sample iris images
def judge_similarity(img, threshold = 0.18, verbose=False):
    samples = get_samples()
    dists =  []
    print 'type of uploaded image is:', type(img)
    print img.shape
    for sam in samples:
        print type(sam), sam.shape
        compare_images(sam, img, verbose=True)
        dists.append(compare_images(sam, img))
    distance = average(dists)
    if verbose:
        print 'Threshold value is:', threshold
        print 'Distance between image and sample images is:', distance
    return distance <= threshold