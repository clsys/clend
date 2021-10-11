from django.conf.urls import url
from chanlun import views

urlpatterns = [
    url(r'^$', views.index, name='index'), ]
