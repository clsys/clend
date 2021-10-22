from django.conf.urls import url
from django.urls import path

from user import views

urlpatterns = [
    url(r'^login', views.login, name='login'),
    url(r'^getInfo', views.getInfo, name='getInfo'),
    url(r'^logout', views.logout, name='logout'),
]
