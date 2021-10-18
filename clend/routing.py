# chat/routing.py
from django.urls import re_path

from chanlun import websocket

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<room_name>\w+)/$', websocket.ChatConsumer.as_asgi()),
]
