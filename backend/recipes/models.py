from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import MinLengthValidator
User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(max_length=64,
                            verbose_name='имена ингредиентов',
                            validators=[MinLengthValidator(
                                1, message='Введите имя')])

    units = models.CharField(max_length=16,
                             verbose_name='меры',
                             validators=[MinLengthValidator(
                                1, message='Введите количество')])

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=64,
                            unique=True,
                            verbose_name='названия тэгов',
                            validators=[MinLengthValidator(
                                1, message='Введите имя')],)

    color_hex = models.CharField(max_length=7,
                                 default='#49B64E',
                                 unique=True,
                                 verbose_name='цвета тэгов')

    slug = models.SlugField(unique=True,
                            max_length=50,
                            db_index=True,
                            verbose_name='slug')

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    owner = models.ForeignKey(User, related_name='recipe_owners',
                              on_delete=models.CASCADE)

    name = models.CharField(max_length=16,
                            verbose_name='имена рецептов',
                            validators=[MinLengthValidator(
                                1, message='Введите имя')])

    image = models.ImageField(upload_to='recipes/images/',
                              null=True,
                              default=None,
                              verbose_name='изображения рецептов')

    description = models.TextField(null=True,
                                   blank=True,
                                   verbose_name='описания рецептов')

    ingredients = models.ManyToManyField(Ingredient,
                                         through='IngredientRecipe',
                                         related_name='recipe_ingredients')
    tags = models.ManyToManyField(Tag,
                                  through='TagRecipe',
                                  related_name='recipe_tags')

    time = models.CharField(max_length=16,
                            verbose_name='время приготавления',
                            validators=[MinLengthValidator(
                                1, 'Введите время')])

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE,
                                   related_name='ingredient_ingredients')

    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='ingredient_recipe')

    amount = models.CharField(max_length=16, default=0,
                              verbose_name='меры',
                              validators=[MinLengthValidator(
                                  1, message='Введите количество')])

    class Meta:
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количиство ингридиентов'

    def __str__(self):
        return f'{self.ingredient} {self.recipe}'


class TagRecipe(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE,
                            related_name='tag_tags')

    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='tag_recipe')

    class Meta:
        verbose_name = 'Тэг рецепта'
        verbose_name_plural = 'Тэги рецептов'

    def __str__(self):
        return f'{self.tag} {self.recipe}'


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='follower')

    following = models.ForeignKey(User, on_delete=models.CASCADE,
                                  related_name='following')

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='user')

    favorite = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                                 related_name='favorite')

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'


class Shopping_list(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='recipe_shopping_list')

    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='user_shopping_list')

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
