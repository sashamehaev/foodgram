import base64

from djoser.serializers import UserSerializer
from django.contrib.auth.password_validation import validate_password
from django.core.validators import RegexValidator
from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from users.models import (
    User,
    Subscription,
    Tag,
    ShoppingCart,
    Ingredient,
    Recipe,
    RecipeIngredient,
    Favorite
)


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='image.' + ext)

        return super().to_internal_value(data)


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()
    avatar = serializers.ImageField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'avatar',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        is_subscribed = Subscription.objects.filter(
            user=request.user, author=obj).exists()
        if is_subscribed:
            return True
        return False


class UserCreateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=150,
        validators=[RegexValidator(
            regex=r'^[\w.@+-]+\Z',
            message='Enter a valid username.'
        )]
    )
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        allow_blank=False,
        error_messages={
            'blank': 'Password cannot be empty.',
            'min_length': 'Password must be at least 8 characters long.'
        },
        validators=[validate_password]
    )

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'password',
        )

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = ('avatar',)


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RetrieveRecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def get_ingredients(self, obj):
        ingredients = []
        for recipe in obj.ingredients_in_recipe.all():
            if recipe.ingredient is not None:
                ingredients.append({
                    'id': recipe.ingredient.id,
                    'name': recipe.ingredient.name,
                    'measurement_unit': recipe.ingredient.measurement_unit,
                    'amount': recipe.amount
                })
        return ingredients

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Favorite.objects.filter(user=user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(user=user, recipe=obj).exists()

    def get_image(self, obj):
        if obj.image:
            return obj.image.url
        return ''


class CreateRecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class CreateRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    ingredients = CreateRecipeIngredientSerializer(many=True)

    def to_representation(self, instance):
        return RetrieveRecipeSerializer(instance, context=self.context).data

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient in ingredients:
            get_ingredient = Ingredient.objects.get(pk=ingredient['id'].id)
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=get_ingredient,
                amount=ingredient['amount']
            )
        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)
        ingredients = validated_data.pop('ingredients', None)
        recipe = super().update(instance, validated_data)

        if ingredients is None:
            raise serializers.ValidationError(
                {'ingredients': 'Поле обязательно.'})
        if tags is None:
            raise serializers.ValidationError({'tags': 'Поле обязательно.'})

        for ingredient in ingredients:
            get_ingredient = Ingredient.objects.get(pk=ingredient['id'].id)
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=get_ingredient,
                amount=ingredient['amount']
            )
        recipe.tags.set(tags)

        return recipe

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'ingredients', 'name', 'image',
            'text', 'cooking_time'
        )
        read_only_fields = ('author',)


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Favorite
        fields = ('__all__')
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe')
            )
        ]


class RecipeShortInfoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscription
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'avatar', 'recipes', 'recipes_count'
        )
        validators = [
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=('user', 'author')
            )
        ]


class RetrieveSubscriptionSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    avatar = serializers.ImageField(read_only=True)
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
            'avatar'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return Subscription.objects.filter(
            user=request.user, author=obj).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes = obj.recipe_author.all()
        limit = request.query_params.get('recipes_limit')
        if limit and limit.isdigit():
            recipes = recipes[:int(limit)]
        return RecipeShortInfoSerializer(recipes, many=True,
                                         context={'request': request}).data


class ShoppingCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShoppingCart
        fields = ('__all__')
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=('user', 'recipe')
            )
        ]


class CreateSubscriptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscription
        fields = ('author',)

    def validate(self, data):
        user = self.context['request'].user
        author = data['author']

        if user == author:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя.'
            )
        if Subscription.objects.filter(user=user, author=author).exists():
            raise serializers.ValidationError(
                'Вы уже подписаны.'
            )
        return data

    def create(self, validated_data):
        return Subscription.objects.create(**validated_data)
