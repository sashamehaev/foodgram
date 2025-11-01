from django.contrib import admin

from .models import (Tag, Recipe, Subscription, Ingredient, User)

admin.site.register(Tag)
admin.site.register(Recipe)
admin.site.register(Subscription)
admin.site.register(Ingredient)
admin.site.register(User)
