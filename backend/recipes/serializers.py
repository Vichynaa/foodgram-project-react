import base64
import webcolors
from django.core.files.base import ContentFile
from rest_framework import serializers
from .models import Tag, TagRecipe, IngredientRecipe,  Ingredient, Recipe
from django.contrib.auth import get_user_model

User = get_user_model()


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
    i_name = serializers.CharField(source='name')
    i_quantity = serializers.CharField(source='quantity')
    i_units = serializers.CharField(source='units')

    class Meta:
        model = Ingredient
        fields = ('id', 'i_name', 'i_quantity', 'i_units')


class TagSerializer(serializers.ModelSerializer):
    t_name = serializers.CharField(source='name')
    t_color = Hex2NameColor()
    t_slug = serializers.SlugField(source='slug')

    class Meta:
        model = Ingredient
        fields = ('id', 't_name', 't_color', 't_slug')


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=False, allow_null=True)
    ingredients = IngredientSerializer(required=False, many=True)
    tags = TagSerializer(required=False, many=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'owner', 'name', 'image', 'description', 'ingredients',
            'tags', 'time'
        )
        read_only_fields = ('owner',)

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

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)

        if 'ingredients' not in validated_data:
            instance.save()
            return instance

        if 'tags' not in validated_data:
            instance.save()
            return instance

        ingredients_data = validated_data.pop('ingredients')
        lst = []
        for ingredient in ingredients_data:
            current_ingredient, status = Ingredient.objects.get_or_create(
                **ingredient
            )
            lst.append(current_ingredient)
        instance.ingredient.set(lst)

        tags_data = validated_data.pop('tags')
        lst = []
        for tag in tags_data:
            current_tag, status = Tag.objects.get_or_create(
                **tag
            )
            lst.append(current_tag)
        instance.tag.set(lst)

        instance.save()
        return instance


class RegistrationSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('email', 'username')

    def validate(self, data):
        # Проверяем, есть ли уже пользователь с таким именем
        username = data.get('username')
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError(
                'Пользователь с таким именем уже зарегистрирован'
            )

        # Проверяем, есть ли уже пользователь с таким email
        email = data.get('email')
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                'Пользователь с таким email уже зарегистрирован'
            )

        # Валидируем, что пользователь не будет использовать никнейм,
        # конфликтующий с эндпоинтом
        if username != 'me':
            return data

        raise serializers.ValidationError('Невозможное имя пользователя')


class ObtainTokenSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=50)
    confirmation_code = serializers.CharField(max_length=15)

    class Meta:
        model = User
        fields = ('username', 'confirmation_code')
