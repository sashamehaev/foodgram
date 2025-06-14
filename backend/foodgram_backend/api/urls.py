from django.urls import path, include
from rest_framework import routers

from api.views import CustomUserViewSet, TagViewSet

router = routers.DefaultRouter()
router.register('users', CustomUserViewSet, basename='user')
router.register('tags', TagViewSet, basename='tag')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]