from django.conf.urls import url
from django.contrib import admin
from upload_app import views

app_name = 'upload_app'

urlpatterns = [
	url(r'^$', views.index, name='index'), 
	url(r'^intro/', views.intro, name='intro'),
	url(r'^register/', views.register, name='register'),
	url(r'^login/', views.user_login, name='user_login'),
	url(r'^logout/', views.user_logout, name='user_logout'),
	url(r'^special/', views.special, name='special'),
	url(r'^upload/', views.upload, name='upload'), 
    # url(r'^admin/', admin.site.urls),
]