from rest_framework import viewsets, status, permissions
from django.db.models import Sum
from django.http import HttpResponse
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import ValidationError
from djoser.serializers import SetPasswordSerializer
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend

from users.serializers import (
    CustomUserSerializer,
    UserCreateSerializer,
    CreateRecipeSerializer,
    AvatarSerializer,
    SubscriptionSerializer,
    TagSerializer,
    IngredientSerializer,
    RetrieveRecipeSerializer,
    RecipeShortInfoSerializer,
    RetrieveSubscriptionSerializer,
    FavoriteSerializer,
    ShoppingCartSerializer
)
from api.permissions import IsAuthorOrReadOnly
from api.filters import IngredientFilter, RecipeFilter
from users.models import Subscription, Tag, Ingredient, Recipe, Favorite, ShoppingCart, RecipeIngredient

User = get_user_model()

class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        if self.action in ['subscriptions', 'subscribe']:
            return SubscriptionSerializer
        return CustomUserSerializer

    @action(methods=['PUT', 'DELETE'], detail=False, url_path='me/avatar', permission_classes=[IsAuthenticated])
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

    @action(methods=['POST', 'DELETE'], detail=True, permission_classes=[IsAuthenticated])
    def subscribe(self, request, pk=None):
        author = get_object_or_404(User, pk=pk)

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

    @action(methods=['GET'], detail=False, permission_classes=[IsAuthenticated])
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
    
    @action(methods=['GET'], detail=False, permission_classes=[IsAuthenticated])
    def me(self, request):
        serializer = self.get_serializer(
            request.user, context={'request': request})
        return Response(serializer.data)
    
    @action(methods=['POST'], detail=False, permission_classes = [IsAuthenticated])
    def set_password(self, request):
        serializer = SetPasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)

        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

        
class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny]
    pagination_class = None
    lookup_field = 'id'

class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [AllowAny]
    pagination_class = None
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter

class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RetrieveRecipeSerializer
    permission_classes = [IsAuthorOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter
    lookup_field = 'id'

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return RetrieveRecipeSerializer
        return CreateRecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(methods=['POST', 'DELETE'], detail=True)
    def favorite(self, request, id=None):
        recipe = get_object_or_404(Recipe, id=id)

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

    @action(methods=['POST', 'DELETE'], detail=True)      
    def shopping_cart(self, request, id=None):
        recipe = get_object_or_404(Recipe, id=id)

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

    @action(methods=['GET'], detail=False, permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        ingredients = (
            ShoppingCart.objects
            .filter(user=request.user)
            .values('recipe__ingredients__name', 'recipe__ingredients__measurement_unit')
            .annotate(total_amount=Sum('recipe__ingredients_in_recipe__amount'))
        )
        content = 'Список покупок:\n'
        for ingredient in ingredients:
            content += (
                f'{ingredient["recipe__ingredients__name"]} '
                f'{ingredient["recipe__ingredients__measurement_unit"]} '
                f'{ingredient["total_amount"]}\n'
            )
        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="shopping_list.txt"'
        return response

    @action(methods=['GET'], detail=True, url_path='get-link')
    def get_link(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        short_link = request.build_absolute_uri(f'/recipes/{recipe.id}/')
        return Response({'short-link': short_link})
