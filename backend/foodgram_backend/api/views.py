from rest_framework import viewsets, status
from django.db.models import Count, Sum, Avg, Max, Min
from django.db import IntegrityError
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from djoser.views import UserViewSet

from users.serializers import (
    CustomUserSerializer,
    CreateRecipeSerializer,
    AvatarSerializer,
    SubscriptionSerializer,
    TagSerializer,
    IngredientSerializer,
    RecipeSerializer,
    RetrieveRecipeSerializer,
    RecipeShortInfoSerializer,
    RetrieveSubscriptionSerializer,
    FavoriteSerializer,
    ShoppingCartSerializer
)
from users.models import Subscription, Tag, Ingredient, Recipe, Favorite, ShoppingCart, RecipeIngredient

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

    @action(methods=('POST', 'DELETE'), detail=True)
    def subscribe(self, request, id=None):
        author = get_object_or_404(User, pk=id)

        if request.method == 'POST':
            serializer = SubscriptionSerializer(
                data={'user': request.user.id, 'author': author.id}
            )
            try:
                serializer.is_valid(raise_exception=True)
            except ValidationError:
                return Response(
                    {"detail": "Вы уже подписаны на пользователя"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer.save()
            return Response(
                RetrieveSubscriptionSerializer(author, context={'request': request}).data,
                status=status.HTTP_201_CREATED
            )
        if request.method == 'DELETE':
            try:
                is_subscribed = Subscription.objects.get(author_id=author.id)
            except Subscription.DoesNotExist:
                return Response(
                    {"detail": "Вы не были подписаны на пользователя"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            is_subscribed.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(methods=('GET', ), detail=False)
    def subscriptions(self, request):
        subscriptions = Subscription.objects.filter(user_id=request.user.id)
        authors = []
        for subscription in subscriptions:
            authors.append(subscription.author)
        return Response(
            RetrieveSubscriptionSerializer(
                authors,
                many=True,
                context={'request': request}
            ).data)

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer

class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateRecipeSerializer
        return RetrieveRecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(methods=('POST', 'DELETE'), detail=True)
    def favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)

        if request.method == 'POST':
            serializer = FavoriteSerializer(data={'user': request.user.id, 'recipe': recipe.pk})
            try:
                serializer.is_valid(raise_exception=True)
            except ValidationError:
                return Response({"detail": "Рецепт в избранном"}, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response(
                RecipeShortInfoSerializer(recipe, context={'request': request}).data,
                status=status.HTTP_201_CREATED
            )
        if request.method == 'DELETE':
            try:
                recipe_in_favorite = Favorite.objects.get(recipe_id=recipe.id)
            except Favorite.DoesNotExist:
                return Response({"detail": "Рецепта нет в избранном"}, status=status.HTTP_400_BAD_REQUEST)
            recipe_in_favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=('POST', 'DELETE'), detail=True)      
    def shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)

        if request.method == 'POST':
            serializer = ShoppingCartSerializer(data={'user': request.user.id, 'recipe': recipe.pk})
            try:
                serializer.is_valid(raise_exception=True)
            except ValidationError:
                return Response(
                    {"detail": "Рецепт уже есть в списке покупок"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer.save()
            return Response(
                RecipeShortInfoSerializer(recipe, context={'request': request}).data,
                status=status.HTTP_201_CREATED
            )
        if request.method == 'DELETE':
            try:
                recipe_in_shopping_cart = ShoppingCart.objects.get(recipe_id=recipe.id)
            except ShoppingCart.DoesNotExist:
                return Response(
                    {"detail": "Рецепта нет в списке покупок"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            recipe_in_shopping_cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=('GET', ), detail=False)
    def download_shopping_cart(self, request):
        user = request.user
        ingredients = (
            RecipeIngredient.objects
            .filter(recipe__shopping_cart__user=user)
            .values('ingredient__name', 'ingredient__measurement_unit')
            .annotate(total_amount=Sum('amount'))
        )
        content = ''
        for ingredient in ingredients:
            content += f"{ingredient['ingredient__name']} {ingredient['total_amount']} {ingredient['ingredient__measurement_unit']}"
        print(content)
        response = Response(content, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="shopping_list.txt"'
        return response
