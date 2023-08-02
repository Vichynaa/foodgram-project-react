from datetime import datetime as dt
from typing import TYPE_CHECKING

from django.apps import apps
from django.db.models import F, Sum
from foodgram.settings import DATE_FORMAT
from recipes.models import IngredientRecipe, Recipe

if TYPE_CHECKING:
    from recipes.models import Ingredient
    from django.contrib.auth import get_user_model
    User = get_user_model()


def recipe_ingredients_set(
    recipe: Recipe, ingredients: dict[int, tuple["Ingredient", int]]
) -> None:
    objs = []

    for ingredient, amount in ingredients.values():
        objs.append(
            IngredientRecipe(
                recipe=recipe, ingredients=ingredient, amount=amount
            )
        )

    IngredientRecipe.objects.bulk_create(objs)


def create_shoping_list(user: "User"):

    shopping_list = [
        f"Список покупок для:\n\n{user.first_name}\n"
        f"{dt.now().strftime(DATE_FORMAT)}\n"
    ]
    Ingredient = apps.get_model("recipes", "Ingredient")
    ingredients = (
        Ingredient.objects.filter(recipe__recipe__in_carts__user=user)
        .values("name", units=F("units"))
        .annotate(amount=Sum("recipe__amount"))
    )
    ingredients_list = (
        f'{i["name"]}: {i["amount"]} {i["units"]}'
        for i in ingredients
    )
    shopping_list.extend(ingredients_list)
