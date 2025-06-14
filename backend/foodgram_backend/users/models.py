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

class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        related_name='subscriptions',
        on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        User,
        related_name='subscribers',
        on_delete=models.CASCADE
    )

class Tag(models.Model):
    name = models.CharField(max_length=32, unique=True)
    slug = models.SlugField(max_length=32, unique=True)
