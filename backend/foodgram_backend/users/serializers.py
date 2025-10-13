import base64
import json
from djoser.serializers import UserSerializer
from django.core.files.base import ContentFile
from rest_framework import serializers
from users.models import (
    User,
    Subscription,
    Tag, 
    TagRecipe,
    Ingredient,
    Recipe,
    RecipeIngredient
)

class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')  
            ext = format.split('/')[-1]  
            data = ContentFile(base64.b64decode(imgstr), name='image.' + ext)

        return super().to_internal_value(data)

class CustomUserSerializer(UserSerializer):
    """ is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        is_subscribed = Subscription.objects.filter(
                user=request.user, author=obj
            ).exists()
        if is_subscribed:
            return True
        return False """

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'avatar', 'is_subscribed')

class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = ('avatar',)

class SubscriptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'email', 
            'id', 
            'username', 
            'first_name', 
            'last_name', 
            'avatar',
            'is_subscribed',
        )

class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'

class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'

class RecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = '__all__'
        read_only_fields = ('author',)

class RetrieveRecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = ('__all__'
            #'id',
            #'author',
            #'tags',
            #'image',
            #'name',
            #'cooking_time',
            #'text',
            #'ingredients'
        )

""" class TagRecipeSerializer(serializers.ModelSerializer):  
    
    def create(self, validated_data):
        if 'tags' in self.initial_data:
            tags = validated_data['tags'].pop()
            print(type(tags))
        
        return self.validated_data

    class Meta:
        model = TagRecipe
        fields = '__all__' """

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
        return RetrieveRecipeSerializer(instance).data

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient in ingredients:
            get_ingredient = Ingredient.objects.get(pk=ingredient['id'].id)
            print(get_ingredient)
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=get_ingredient,
                amount=ingredient['amount']
            )
        recipe.tags.set(tags)
        return recipe


    class Meta:
        model = Recipe
        fields = ('__all__'
            #'tags',
            #'image',
            #'name',
            #'cooking_time',
            #'text',
            #'ingredients'
        )
        read_only_fields = ('author',)


""" class RecipeIngredientSerializer(serializers.ModelSerializer):

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')

class RecipeReadSerializer(serializers.ModelSerializer):
    
    author = CustomUserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        source='recipeingredient_set',
        many=True,
        read_only=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return obj.favorites.filter(user=request.user).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return obj.shopping_cart.filter(user=request.user).exists()

class RecipeCreateSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    tags = TagSerializer(many=True)
    ingredients = IngredientSerializer(many=True)

    def create(self, validated_data):
        #tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient in ingredients:
            RecipeIngredient.objects.create(recipe=recipe, ingredient=ingredient['id'], amount=ingredient['amount'])
        return recipe


    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'text', 'ingredients', 'cooking_time', 'tags') """