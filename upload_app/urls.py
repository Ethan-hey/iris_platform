from django.conf.urls import url
from django.contrib import admin
from upload_app import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'upload_app'

urlpatterns = [
	url(r'^$', views.index, name='index'), 
	url(r'^intro/', views.intro, name='intro'),
	url(r'^register/', views.register, name='register'),
	url(r'^login/', views.user_login, name='user_login'),
	url(r'^logout/', views.user_logout, name='user_logout'),
	url(r'^special/', views.special, name='special'),
	url(r'^upload/', views.upload, name='upload'), 
	url(r'^iris gallery/', views.iris_gallery, name='iris_gallery'), 
	url(r'^upload_face/', views.upload_face, name='upload_face'), 
	url(r'^face_gallery/', views.face_gallery, name='face_gallery'), 
    # url(r'^admin/', admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
