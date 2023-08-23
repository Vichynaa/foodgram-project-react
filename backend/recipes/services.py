from datetime import datetime as dt
from typing import TYPE_CHECKING
from rest_framework import status
from rest_framework.generics import get_object_or_404
from .models import Recipe
from django.shortcuts import HttpResponse
from rest_framework.response import Response

if TYPE_CHECKING:
    from django.contrib.auth import get_user_model
    User = get_user_model()


def add_del_for_shopping_follow_favorite(serializer, model, request, r_id):
    user = request.user
    recipe = get_object_or_404(Recipe, id=r_id)
    if request.method == 'POST':
        recipe_data = {'user': user.id, 'recipe': recipe.id}
        serializer = serializer(data=recipe_data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    obj_to_delete = get_object_or_404(model, user=user, recipe=recipe)
    obj_to_delete.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


def create_shopping_list(request, ingredients):
    user = request.user
    filename = f'{user.username}_shopping_list.txt'
    today = dt.today()

    shopping_list = [
        f'{ingredient["ingredient__name"]} '
        f'{ingredient["ingredient__measurement_unit"]} '
        f'{ingredient["amount"]}'
        for ingredient in ingredients
    ]

    shopping_list_content = (
        f'Список покупок: {user.username}\n'
        f'Дата: {today:%Y-%m-%d}\n\n'
        '\n'.join(shopping_list) + f'\n\nFoodgram ({today:%Y})'
    )

    response = HttpResponse(
        shopping_list_content, content_type='text/plain; charset=utf-8'
    )
    response['Content-Disposition'] = f'attachment; filename={filename}'
    return response
