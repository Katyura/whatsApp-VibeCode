from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.status.views import StatusViewSet

router = DefaultRouter()
router.register(r'', StatusViewSet, basename='status')

urlpatterns = [
    path('', include(router.urls)),
]
