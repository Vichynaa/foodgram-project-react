from django_filters.rest_framework import FilterSet
from django_filters import rest_framework
from .models import Recipe, Tag
from rest_framework import filters


class CustomRecipesSearchFilter(FilterSet):
    tags = rest_framework.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug')
    is_favorited = rest_framework.BooleanFilter(method='filter_favorited')
    is_in_shopping_cart = rest_framework.BooleanFilter(
        method='filter_shopping_list')

    def filter_favorited(self, queryset, nothing, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(favorite__user=self.request.user)
        return queryset

    def filter_shopping_list(self, queryset, nothing, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(shopping_lists__user=self.request.user)
        return queryset

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')


class IngredientSearchFilter(filters.SearchFilter):
    search_param = 'name'
