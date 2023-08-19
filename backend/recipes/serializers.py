import base64
import webcolors
from django.core.files.base import ContentFile
from rest_framework import serializers
from .models import Tag, TagRecipe, IngredientRecipe
from .models import Follow, Ingredient, Recipe, Favorite, Shopping_list
from rest_framework.validators import UniqueTogetherValidator
from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'password')
        extra_kwargs = {'email': {'required': True},
                        'username': {'required': True}}

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class AdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name', 'password'
        )


class Hex2NameColor(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError('Для этого цвета нет имени')
        return data


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('__all__')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('__all__')


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.CharField(read_only=True, source='ingredient.name')
    measurement_unit = serializers.CharField(
        read_only=True, source='ingredient.measurement_unit')

    class Meta:
        model = IngredientRecipe
        fields = ['id', 'amount', 'name', 'measurement_unit']


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('__all__')

    def get_favorite(self, instance):
        request = self.context.get('request')
        return (request and request.user.is_authenticated
                and request.user.favorite.filter(recipe=instance).exists())

    def get_shopping(self, instance):
        request = self.context.get('request')
        return (request and request.user.is_authenticated
                and request.user.shopping_lists.filter(recipe=instance).exists())

    def get_ingredients(self, instance):
        return IngredientRecipeSerializer(
            instance.ingredient_recipe.all(),
            many=True).data


class FollowSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(
        read_only=True, default=serializers.CurrentUserDefault())
    following = serializers.SlugRelatedField(slug_field='username',
                                             queryset=User.objects.all())

    class Meta:
        model = Follow
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'following')
            )
        ]

    def validate(self, data):
        if self.context['request'].user == data['following']:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя!')
        return data


class FavoriteSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(
        read_only=True, default=serializers.CurrentUserDefault())
    favorite = serializers.SlugRelatedField(slug_field='favorite',
                                            queryset=Favorite.objects.all())

    class Meta:
        model = Favorite
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'favorite')
            )
        ]


class ShoppinglistSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(
        read_only=True, default=serializers.CurrentUserDefault())
    recipe = serializers.SlugRelatedField(slug_field='recipe',
                                          queryset=Recipe.objects.all())

    class Meta:
        model = Shopping_list
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Shopping_list.objects.all(),
                fields=('user', 'recipe')
            )
        ]


class RecipeCreateIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    name = serializers.CharField(read_only=True, source='ingredient.name')
    measurement_unit = serializers.CharField(
        read_only=True, source='ingredient.measurement_unit')

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount', 'name', 'measurement_unit')


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = RecipeCreateIngredientSerializer(many=True)
    image = Base64ImageField()
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True)
    author = UserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = ('name', 'cooking_time', 'text', 'tags', 'ingredients',
                  'image', 'author')

    def create_ingredients(self, instance, ingredients):
        for ingredient in ingredients:
            IngredientRecipe.objects.create(
                recipe=instance,
                ingredient=ingredient['id'],
                amount=ingredient['amount']
            )

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(recipe, ingredients)
        return recipe
