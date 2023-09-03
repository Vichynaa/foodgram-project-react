from django.contrib import admin
from .models import Ingredient, IngredientRecipe, Recipe, Tag
from .models import Follow, Favorite, Shopping_list, TagRecipe


class IngredientRecipeInline(admin.TabularInline):
    model = IngredientRecipe


class TagRecipeInline(admin.TabularInline):
    model = TagRecipe


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'text')
    search_fields = ('name', 'author__username')
    list_filter = ('author__username', 'text')
    inlines = [IngredientRecipeInline, TagRecipeInline]


admin.site.register(Ingredient)
admin.site.register(Tag)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Follow)
admin.site.register(Favorite)
admin.site.register(Shopping_list)
