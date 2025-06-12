from djoser.serializers import UserSerializer
from rest_framework import serializers
from users.models import User

class CustomUserSerializer(UserSerializer):
    avatar = serializers.ImageField(required=False)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'avatar')