from django.urls import path, include
from rest_framework import routers

from api.views import CustomUserViewSet

router = routers.DefaultRouter()
router.register('users', CustomUserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]