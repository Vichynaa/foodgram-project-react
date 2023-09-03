from django.contrib import admin
from .models import Ingredient, IngredientRecipe, Recipe, Tag
from .models import Follow, Favorite, Shopping_list, TagRecipe


class IngredientRecipeInline(admin.TabularInline):
    model = IngredientRecipe
    min_num = 1


class TagRecipeInline(admin.TabularInline):
    model = TagRecipe
    min_num = 1


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'cooking_time')
    search_fields = ('name', 'author__username')
    list_filter = ('author__username', 'cooking_time')
    inlines = [IngredientRecipeInline, TagRecipeInline]


admin.site.register(Ingredient)
admin.site.register(Tag)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Follow)
admin.site.register(Favorite)
admin.site.register(Shopping_list)
