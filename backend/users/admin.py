from django.contrib import admin

from .models import (
    Tag,
    Recipe,
    Subscription,
    Ingredient,
    User,
    RecipeIngredient,
    TagRecipe
)

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'slug')
    list_display_links = ('name', 'id')
    search_fields = ('name',)
    ordering = ('name',)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


class TagRecipeInline(admin.TabularInline):
    model = TagRecipe
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'author', 'cooking_time')
    list_display_links = ('name', 'id', 'author')
    search_fields = ('name', 'author__username')
    list_filter = ('tags',)
    inlines = [RecipeIngredientInline, TagRecipeInline]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('author').prefetch_related(
            'tags',
            'recipe_ingredients__ingredient'
        )


admin.site.register(Subscription)
admin.site.register(Ingredient)
admin.site.register(User)
