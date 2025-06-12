from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from djoser.views import UserViewSet

from users.serializers import CustomUserSerializer

User = get_user_model()

class CustomUserViewSet(UserViewSet):
    serializer_class = CustomUserSerializer

    def get_queryset(self):
        return User.objects.all()
    

    """@action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)"""

    """@action(detail=False, methods=['put', 'delete'], url_path='me/avatar')
    def avatar(self, request):
        if request.method == 'PUT':
            serializer = SetAvatarSerializer(data=request.data)
            if serializer.is_valid():
                request.user.avatar = serializer.validated_data['avatar']
                request.user.save()
                return Response({
                    'avatar': request.user.avatar.url if request.user.avatar else None
                })
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

        elif request.method == 'DELETE':
            if request.user.avatar:
                request.user.avatar.delete()
                request.user.avatar = None
                request.user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)"""

"""    @action(detail=False, methods=['post'])
    def set_password(self, request):
        user = request.user
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')

        if not current_password or not new_password:
            return Response(
                {'errors': 'Необходимо указать текущий и новый пароль'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Проверка текущего пароля
        if not user.check_password(current_password):
            return Response(
                {'errors': 'Неверный текущий пароль'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Установка нового пароля
        user.set_password(new_password)
        user.save()

        return Response(status=status.HTTP_204_NO_CONTENT)"""

"""    @action(detail=True, methods=['post', 'delete'])
    def subscribe(self, request, pk=None):
        #Подписаться/отписаться от автора.
        try:
            author_id = int(pk)
            author = get_object_or_404(User, pk=author_id)
        except (ValueError, TypeError):
            # Если ID невалидный, возвращаем 400
            return Response(
                {'errors': 'Некорректный ID пользователя'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if request.user == author:
            return Response(
                {'errors': 'Нельзя подписаться на себя'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if request.method == 'POST':
            subscription, created = Subscription.objects.get_or_create(
                user=request.user, author=author
            )
            if created:
                serializer = SubscriptionSerializer(
                    author, context={'request': request}
                )
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
            return Response(
                {'errors': 'Вы уже подписаны на этого пользователя'},
                status=status.HTTP_400_BAD_REQUEST
            )

        subscription = Subscription.objects.filter(
            user=request.user, author=author
        ).first()
        if not subscription:
            return Response(
                {'errors': 'Вы не подписаны на этого пользователя'},
                status=status.HTTP_400_BAD_REQUEST
            )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def subscriptions(self, request):
        # Находим всех авторов, на которых подписан пользователь
        authors = User.objects.filter(
            subscribed__user=request.user
        ).order_by('id')

        page = self.paginate_queryset(authors)
        if page is not None:
            serializer = SubscriptionSerializer(
                page, many=True, context={'request': request}
            )
            return self.get_paginated_response(serializer.data)

        serializer = SubscriptionSerializer(
            authors, many=True, context={'request': request}
        )
        return Response(serializer.data)"""