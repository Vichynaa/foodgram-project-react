from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import MinLengthValidator
User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(max_length=64,
                            verbose_name='имя ингредиента',
                            validators=[MinLengthValidator(
                                1, message='Введите имя')])

    units = models.CharField(max_length=16,
                             verbose_name='мера',
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
                            verbose_name='название_тэга',
                            validators=[MinLengthValidator(
                                1, message='Введите имя')],)
    color_hex = models.CharField(max_length=7,
                                 default='#49B64E',
                                 unique=True,
                                 verbose_name='цвет тэга')
    slug = models.SlugField(
        unique=True,
        max_length=50,
        db_index=True,
        verbose_name='slug')

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    owner = models.ForeignKey(
        User, related_name='рецепты',
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=16,
                            verbose_name='имя_рецепта',
                            validators=[MinLengthValidator(
                                1, message='Введите имя')])
    image = models.ImageField(
        upload_to='recipes/images/',
        null=True,
        default=None,
        verbose_name='изображение рецепта',
    )
    description = models.TextField(null=True,
                                   blank=True,
                                   verbose_name='описание рецепта')
    ingredients = models.ManyToManyField(Ingredient,
                                         through='IngredientRecipe',
                                         related_name='ингредиенты_рецепта')
    tags = models.ManyToManyField(Tag,
                                  through='TagRecipe',
                                  related_name='тэги_рецепта')
    time = models.CharField(max_length=16,
                            verbose_name='время приготавления',
                            validators=[MinLengthValidator(
                                1, 'Введите время')])

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE,
                                   related_name='ингредиенты')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='ингредиенты_для_рецепты')
    amount = models.CharField(max_length=16, default=0,
                              verbose_name='мера',
                              validators=[MinLengthValidator(
                                1, message='Введите количество')])

    def __str__(self):
        return f'{self.ingredient} {self.recipe}'


class TagRecipe(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE,
                            related_name='тэг')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='тэг_рецепта')

    def __str__(self):
        return f'{self.tag} {self.recipe}'


class Follow(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='подписчик'
    )
    following = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='на_кого_подписываются'
    )


class Favorite(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='пользователь'
    )
    favorite = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='избранное'
    )


class Shopping_list(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='рецепт_список_покупок'
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='пользователь_список_покупок'
    )
