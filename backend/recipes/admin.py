from django.contrib import admin
from .models import Ingredient, Tag, Recipe, IngredientRecipe
from .models import TagRecipe, Follow, Favorite, Shopping_list


class IngredientRecipeInline(admin.TabularInline):
    model = IngredientRecipe


class TagRecipeInline(admin.TabularInline):
    model = TagRecipe


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'time')
    search_fields = ('name', 'owner__username')
    list_filter = ('owner__username', 'time')
    inlines = [IngredientRecipeInline, TagRecipeInline]


admin.site.register(Ingredient)
admin.site.register(Tag)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Follow)
admin.site.register(Favorite)
admin.site.register(Shopping_list)
