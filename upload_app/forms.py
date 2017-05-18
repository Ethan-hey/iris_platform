from django import forms
from django.contrib.auth.models import User
from upload_app.models import Document, Document_face

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta():
        model = User
        fields = ('username','email','password')


class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ('username', 'document', )

class DocumentFaceForm(forms.ModelForm):
	class Meta:
		model = Document_face
		fields = ('username', 'document', )