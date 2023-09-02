from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import MinLengthValidator, MinValueValidator
from django.core.exceptions import ValidationError
User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(max_length=64,
                            verbose_name='имена ингредиентов',
                            validators=[MinLengthValidator(
                                1, message='Введите имя')])

    measurement_unit = models.CharField(max_length=16,
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

    color = models.CharField(max_length=7,
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
    author = models.ForeignKey(User, related_name='recipe_authors',
                               on_delete=models.CASCADE)

    name = models.CharField(max_length=32,
                            verbose_name='имена рецептов',
                            validators=[MinLengthValidator(
                                1, message='Введите имя')])

    image = models.ImageField(upload_to='recipes/images',
                              null=True,
                              default=None,
                              verbose_name='изображения рецептов')

    text = models.TextField(null=True,
                            blank=True,
                            verbose_name='описания рецептов')

    ingredients = models.ManyToManyField(Ingredient,
                                         through='IngredientRecipe',
                                         related_name='recipe_ingredients')
    tags = models.ManyToManyField(Tag,
                                  through='TagRecipe',
                                  related_name='recipe_tags')
    pub_date = models.DateTimeField(auto_now_add=True,
                                    verbose_name='дата публикации')

    cooking_time = models.PositiveIntegerField(
        verbose_name='время приготавления',
        validators=[MinValueValidator(
            1, 'Введите время')])

    def clean(self):
        if not self.ingredients.exists():
            raise ValidationError('Должен быть хотя бы один ингредиент')

        if not self.tags.exists():
            raise ValidationError('Должен быть хотя бы один тег')

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE,
                                   related_name='ingredient_recipe')

    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='ingredient_recipe')

    amount = models.PositiveIntegerField(
        verbose_name='количество',
        validators=[MinValueValidator(1, 'Введите количество')])

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
                             related_name='user_favorite')

    favorite = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                                 related_name='favorite')

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'


class Shopping_list(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='shopping_lists')

    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='user_shoppinglist')

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
