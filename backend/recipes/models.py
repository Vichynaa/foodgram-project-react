from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(max_length=64,
                            unique=True)
    quantity = models.CharField(max_length=16,
                                unique=True)
    units = models.CharField(max_length=16,
                             unique=True)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=64,
                            unique=True)
    color_hex = models.CharField(max_length=7,
                                 default='#49B64E',
                                 unique=True)
    slug = models.SlugField(
        unique=True,
        max_length=50,
        db_index=True)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    owner = models.ForeignKey(
        User, related_name='recipes',
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=16)
    image = models.ImageField(
        upload_to='recipes/images/',
        null=True,
        default=None
    )
    description = models.TextField()
    ingredients = models.ManyToManyField(Ingredient,
                                         through='IngredientRecipe')
    tags = models.ManyToManyField(Tag,
                                  through='TagRecipe')
    time = models.CharField(max_length=16)


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.ingredient} {self.recipe}'


class TagRecipe(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

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
