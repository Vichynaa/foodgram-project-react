from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(max_length=64,
                            unique=True,
                            verbose_name='ingredient_name')
    units = models.CharField(max_length=16,
                             unique=True,
                             verbose_name='units')

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=64,
                            unique=True,
                            verbose_name='tag_name')
    color_hex = models.CharField(max_length=7,
                                 default='#49B64E',
                                 unique=True,
                                 verbose_name='tag_color')
    slug = models.SlugField(
        unique=True,
        max_length=50,
        db_index=True,
        verbose_name='slug')

    def __str__(self):
        return self.name


class Recipe(models.Model):
    owner = models.ForeignKey(
        User, related_name='recipes',
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=16,
                            verbose_name='recipe_name')
    image = models.ImageField(
        upload_to='recipes/images/',
        null=True,
        default=None,
        verbose_name='recipe_image'
    )
    description = models.TextField(null=True,
                                   blank=True,
                                   verbose_name='recipe_description')
    ingredients = models.ManyToManyField(Ingredient,
                                         through='IngredientRecipe',
                                         related_name='recipe_ingredients')
    tags = models.ManyToManyField(Tag,
                                  through='TagRecipe',
                                  related_name='recipe_tags')
    time = models.CharField(max_length=16,
                            verbose_name='cooking_time')


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE,
                                   related_name='ingredient_ingredients')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='ingredient_recipe')
    amount = models.CharField(max_length=16, default=0,
                              verbose_name='amount')

    def __str__(self):
        return f'{self.ingredient} {self.recipe}'


class TagRecipe(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE,
                            related_name='tag_tags')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='tag_recipe')

    def __str__(self):
        return f'{self.tag} {self.recipe}'


class Follow(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='follower'
    )
    following = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='following'
    )


class Favorite(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='user'
    )
    favorite = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='favorite'
    )
