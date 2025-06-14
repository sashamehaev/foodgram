from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from djoser.views import UserViewSet

from users.serializers import CustomUserSerializer, AvatarSerializer, SubscriptionSerializer, TagSerializer
from users.models import Subscription, Tag

User = get_user_model()

class CustomUserViewSet(UserViewSet):
    serializer_class = CustomUserSerializer

    def get_queryset(self):
        return User.objects.all()

    @action(detail=False, methods=['put', 'delete'], url_path='me/avatar')
    def avatar(self, request):
        user = request.user
        if request.method == 'PUT':
            serializer = AvatarSerializer(user, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user.avatar.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'])
    def subscribe(self, request, id=None):
        author = get_object_or_404(User, pk=id)

        if request.user == author:
            return Response(
                {'message': 'Нельзя подписаться на самого себя'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if request.method == 'POST':
            _, created_status = Subscription.objects.get_or_create(
                user=request.user, author=author
            )
            if created_status:
                serializer = CustomUserSerializer(author, context={'request': request})
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
            return Response(
                {'message': 'Вы уже подписаны на этого пользователя'},
                status=status.HTTP_400_BAD_REQUEST
            )

        subscription = Subscription.objects.filter(
            user=request.user, author=author
        ).first()
        if not subscription:
            return Response(
                {'message': 'Вы не подписаны на этого пользователя'},
                status=status.HTTP_400_BAD_REQUEST
            )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def subscriptions(self, request):
        authors = User.objects.filter(subscribers__user=request.user)

        serializer = SubscriptionSerializer(
            authors,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)
    
class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    