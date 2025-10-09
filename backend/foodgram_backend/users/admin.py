from django.contrib import admin

from .models import (Tag, Recipe, Subscription, Ingredient)

admin.site.register(Tag)
admin.site.register(Recipe)
admin.site.register(Subscription)
admin.site.register(Ingredient)
#admin.site.register(RecipeIngredient)
