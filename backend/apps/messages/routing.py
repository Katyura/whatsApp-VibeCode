from django.urls import path
from apps.messages.consumers import ChatConsumer, GroupConsumer

websocket_urlpatterns = [
    path('ws/chat/<uuid:chat_id>/', ChatConsumer.as_asgi()),
    path('ws/group/<uuid:group_id>/', GroupConsumer.as_asgi()),
]
