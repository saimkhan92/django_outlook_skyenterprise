from django.conf.urls import url
from tutorial import views

app_name = 'tutorial'
urlpatterns = [
  # The home view ('/tutorial/')
  url(r'^$', views.home, name='home'),
  # Explicit home ('/tutorial/home/')
  url(r'^home/$', views.home, name='home'),
  # Redirect to get token ('/tutorial/gettoken/')
  url(r'^gettoken/$', views.gettoken, name='gettoken'),
  # Mail view ('/tutorial/mail/')
  url(r'^mail/$', views.mail, name='mail'),
  url(r'^download_mail/$', views.download_mail, name='download_mail'),
]
