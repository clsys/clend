from django.conf.urls import url
from django.urls import path

from chanlun import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    path('chat/<str:room_name>/', views.room, name='room'),
    url(r'^dizzy$', views.dizzy, name='dizzy'),
    url(r'^start$', views.start, name='start'),
]
