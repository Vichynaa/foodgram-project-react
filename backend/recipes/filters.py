from django_filters.rest_framework import FilterSet
from django_filters import rest_framework
from .models import Recipe, Tag
from rest_framework import filters


class CustomRecipesSearchFilter(FilterSet):
    tags = rest_framework.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug')

    class Meta:
        model = Recipe
        fields = ('author', 'tags')


class IngredientSearchFilter(filters.SearchFilter):
    search_param = 'name'
