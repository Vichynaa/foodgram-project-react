from django.contrib import admin

from .models import Favorite, Follow, Recipe, Tag, Ingredient


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color_hex', 'slug')


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'units')


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('owner', 'name', 'image', 'description', 'time')


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Follow)
admin.site.register(Favorite)
