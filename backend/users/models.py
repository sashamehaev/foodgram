from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    username = models.CharField(
        max_length=150,
        unique=True
    )
    email = models.EmailField(
        max_length=254,
        unique=True
    )
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    avatar = models.ImageField(upload_to='users/avatar/')
    is_subscribed = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = (
        'username',
        'first_name',
        'last_name',
    )

class Tag(models.Model):
    name = models.CharField(max_length=32, unique=True)
    slug = models.SlugField(max_length=32, unique=True, verbose_name='Slug')

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'
        ordering = ['name']

    def __str__(self):
        return self.name
    

class Ingredient(models.Model):
    name = models.CharField(max_length=128)
    measurement_unit = models.CharField(max_length=64)

class Recipe(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipe_author')
    ingredients = models.ManyToManyField(Ingredient, related_name='recipes', through='RecipeIngredient')
    tags = models.ManyToManyField(Tag, related_name='recipes', through='TagRecipe')
    name = models.CharField(max_length=256)
    image = models.ImageField(upload_to='recipes/image/')
    text = models.TextField()
    cooking_time = models.IntegerField()

class TagRecipe(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, related_name='ingredients_in_recipe', on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.IntegerField()

class Favorite(models.Model):
    recipe = models.ForeignKey(Recipe, related_name='favorited_by', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('recipe', 'user')

class Subscription(models.Model):
    user = models.ForeignKey(User, related_name='user', on_delete=models.CASCADE)
    author = models.ForeignKey(User, related_name='authors', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('author', 'user')

class ShoppingCart(models.Model):
    user = models.ForeignKey(User, related_name='shopping_carts', on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, related_name='shopping_carts', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'recipe')
