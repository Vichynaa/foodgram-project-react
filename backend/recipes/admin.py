from django.contrib import admin

from .models import Favorite, Follow, Recipe, Tag, Ingredient

admin.site.register(Ingredient)
admin.site.register(Tag)
admin.site.register(Recipe)
admin.site.register(Follow)
admin.site.register(Favorite)
