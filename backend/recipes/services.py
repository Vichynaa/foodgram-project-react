from datetime import datetime
from django.shortcuts import HttpResponse


def create_shopping_list(request, ingredients):
    user = request.user
    today = datetime.today()
    filename = f'{today}_for_shopping.txt'

    shopping_list = [
        f'- {ingredient["ingredient__name"]} -> '
        f'{ingredient["amount"]} '
        f'{ingredient["ingredient__measurement_unit"]}'
        for ingredient in ingredients]

    shopping_list_content = (
        f'Список покупок для {user.username} \n \n',
        'Ингредиенты: \n',
        '\n'.join(shopping_list), f'\n\nFoodgram({today:%d/%m/%Y})')

    response = HttpResponse(
        shopping_list_content, content_type='text/plain; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response
