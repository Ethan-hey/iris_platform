from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
import uuid
import os

# Create your models here.

def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'iris/user_{0}/{1}'.format(instance.username, filename)
    # return 'user_{0}/{1}'.format(instance.user.id, filename)


class Document(models.Model):

    username = models.CharField(max_length=255, blank=True)
    # document = models.FileField(upload_to='images/')
    document = models.FileField(upload_to= user_directory_path)

    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.username


class Document_face(models.Model):

    username = models.CharField(max_length=255, blank=True)
    # document = models.FileField(upload_to='images/')
    document = models.FileField(upload_to= user_directory_path)

    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.username