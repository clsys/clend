# demo/urls.py
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^kline', views.kline, name='kline'),
    url(r'^chan', views.chan, name='chan'),
    url(r'^query', views.query, name='query'),
    url(r'^new_gain', views.new_gain, name='new_gain'),
    url(r'^$', views.index, name='index'),
]