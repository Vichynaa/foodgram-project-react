import base64
from django.core.files.base import ContentFile
from rest_framework import serializers
from .models import Tag, IngredientRecipe
from .models import Follow, Ingredient, Recipe, Favorite, Shopping_list
from .models import TagRecipe
from rest_framework.validators import UniqueTogetherValidator
from django.contrib.auth import get_user_model
from rest_framework.validators import UniqueValidator

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    email = serializers.EmailField(validators=[UniqueValidator(
        queryset=User.objects.all(),
        message='Пользователь с такой почтой уже существует')])
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'password', 'is_subscribed')
        extra_kwargs = {'username': {'required': True},
                        'email': {'required': True}}

    def validate(self, data):
        username = data.get('username')
        if username == 'me':
            raise serializers.ValidationError(
                'me - невозможное имя пользователя')
        return data

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

    def get_is_subscribed(self, instance):
        admin_serializer = AdminUserSerializer(instance, context=self.context)
        return admin_serializer.data['is_subscribed']


class AdminUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'password', 'is_subscribed')

    def get_is_subscribed(self, instance):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return request.user.follower.filter(following=instance).exists()
        return False


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('__all__')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('__all__')

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.save()
        return instance


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

    def update(self, instance, validated_data):
        instance.amount = validated_data.get('amount', instance.amount)
        instance.save()
        return instance


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    image = serializers.ReadOnlyField(source='image.url')
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('__all__')

    def get_is_favorited(self, instance):
        request = self.context.get('request')
        return (request and request.user.is_authenticated
                and request.user.user_favorite.filter(
                    favorite=instance).exists())

    def get_is_in_shopping_cart(self, instance):
        request = self.context.get('request')
        return (request and request.user.is_authenticated
                and request.user.user_shoppinglist.filter(
                    recipe=instance).exists())

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
        following = self.instance
        user = self.context.get('request').user
        if Follow.objects.filter(user=user, following=following).exists():
            raise serializers.ValidationError(
                'Вы уже подписаны на этого пользователя'
            )
        if self.context['request'].user == data['following']:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя!')
        return data


class FavoriteSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    favorite = serializers.SlugRelatedField(slug_field='favorite',
                                            queryset=Favorite.objects.all())

    class Meta:
        model = Favorite
        fields = ('__all__')
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'favorite'))]


class ShoppinglistSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    recipe = serializers.SlugRelatedField(slug_field='recipe',
                                          queryset=Recipe.objects.all())

    class Meta:
        model = Shopping_list
        fields = ('__all__')
        validators = [
            UniqueTogetherValidator(
                queryset=Shopping_list.objects.all(),
                fields=('user', 'recipe'))]


class RecipeCreateIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    name = serializers.CharField(read_only=True, source='ingredient.name')
    measurement_unit = serializers.CharField(
        read_only=True, source='ingredient.measurement_unit')

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount', 'name', 'measurement_unit')


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = RecipeCreateIngredientSerializer(many=True,
                                                   source='ingredient_recipe',
                                                   required=True)
    image = Base64ImageField()
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                              many=True, required=True)
    author = UserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'cooking_time', 'text', 'tags', 'ingredients',
                  'image', 'author')

    def create_ingredients(self, instance, ingredients_data):
        for ingredient in ingredients_data:
            IngredientRecipe.objects.create(
                recipe=instance,
                ingredient=ingredient['id'],
                amount=ingredient['amount']
            )

    def create_tags(self, instance, tags_data):
        for tag in tags_data:
            TagRecipe.objects.create(tag=tag, recipe=instance)

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredient_recipe')
        recipe = Recipe.objects.create(**validated_data)
        self.create_ingredients(recipe, ingredients)
        self.create_tags(recipe, tags)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredient_recipe')
        TagRecipe.objects.filter(recipe=instance).delete()
        IngredientRecipe.objects.filter(recipe=instance).delete()
        self.create_ingredients(instance, ingredients)
        self.create_tags(instance, tags)
        return super().update(instance, validated_data)

    def validate(self, data):
        tags = data.get('tags')
        ingredients = data.get('ingredient_recipe')
        if not ingredients:
            raise serializers.ValidationError('Добавьте ингредиент')

        if not tags:
            raise serializers.ValidationError('Добавьте тэг')

        return data


class SubscriptionSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta(UserSerializer.Meta):
        fields = ('recipes', 'recipes_count') + UserSerializer.Meta.fields

    def get_recipes(self, author):
        recipes = Recipe.objects.filter(author=author)[:3]
        recipe_serializer = RecipeSerializer(
            recipes, many=True, context=self.context)
        return recipe_serializer.data

    def get_recipes_count(self, instance):
        return instance.recipe_authors.count()


class RecipeFavoriteaAndShoppingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
