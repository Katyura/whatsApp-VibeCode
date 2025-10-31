from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.messages.views import ChatViewSet, GroupViewSet, MessageViewSet

router = DefaultRouter()
router.register(r'chats', ChatViewSet, basename='chats')
router.register(r'groups', GroupViewSet, basename='groups')
router.register(r'', MessageViewSet, basename='messages')

urlpatterns = [
    path('', include(router.urls)),
]
