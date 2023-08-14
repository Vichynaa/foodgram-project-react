from rest_framework.serializers import SerializerMethodField
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
    ingredient_name = serializers.CharField(source='name')
    ingredient_quantity = serializers.CharField(source='quantity')
    ingredient_units = serializers.CharField(source='units')

    class Meta:
        model = Ingredient
        fields = ('id', 'ingredient_name', 'ingredient_quantity',
                  'ingredient_units')


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


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    owner = UserSerializer(read_only=True)
    ingredients = SerializerMethodField()
    favorite = SerializerMethodField()
    shopping = SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('__all__')
        read_only_fields = ('favorite', 'shopping')

    def create_tags(self, validated_data):
        if 'tags' not in self.initial_data:
            recipe = Recipe.objects.create(**validated_data)
            return recipe
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        for tag in tags:
            current_tag, status = Tag.objects.get_or_create(
                **tag
            )
            TagRecipe.objects.create(
                tag=current_tag, recipe=recipe
            )
        return recipe

    def create_ingredients(self, validated_data):
        if 'ingredients' not in self.initial_data:
            recipe = Recipe.objects.create(**validated_data)
            return recipe
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient in ingredients:
            current_ingredient, status = Ingredient.objects.get_or_create(
                **ingredient
            )
            IngredientRecipe.objects.create(
                ingredient=current_ingredient, recipe=recipe
            )
        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description',
                                                  instance.description)
        instance.time = validated_data.get(
            'time', instance.time
        )
        instance.image = validated_data.get('image', instance.image)
        instance.save()
        return instance

    def update_tags(self, instance, validated_data):
        if 'tags' not in validated_data:
            instance.save()
            return instance

        tags_data = validated_data.pop('tags')
        tag_list = [Tag.objects.get_or_create(**tag) for tag in tags_data]
        instance.tags.set(tag_list)
        instance.save()
        return instance

    def update_ingredients(self, instance, validated_data):
        if 'ingredients' not in validated_data:
            instance.save()
            return instance

        ingredients_data = validated_data.pop('ingredients')
        ingredient_list = [Ingredient.objects.get_or_create(
            **ingredient) for ingredient in ingredients_data]
        instance.ingredients.set(ingredient_list)

        instance.save()
        return instance

    def get_favorite(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.favorite.filter(user=request.user).exists()
        return False

    def get_shopping(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.shopping.filter(user=request.user).exists()
        return False

    def get_ingredients(self, obj):
        ingredients = IngredientRecipe.objects.filter(recipe=obj)
        ingredient_data = [
            {
                'id': ingredient.id,
                'name': ingredient.ingredient.name,
                'amount': ingredient.amount
            }
            for ingredient in ingredients
        ]
        return ingredient_data


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
