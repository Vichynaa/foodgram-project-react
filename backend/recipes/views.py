from rest_framework import viewsets
from .models import Recipe, Tag, Ingredient, Follow, Favorite, Shopping_list
from .models import IngredientRecipe
from .serializers import RecipeSerializer, TagSerializer, IngredientSerializer
from .serializers import FollowSerializer, FavoriteSerializer
from .serializers import UserSerializer, RecipeFavoriteaAndShoppingSerializer
from .serializers import RecipeCreateSerializer, SubscriptionSerializer
from rest_framework import permissions
from rest_framework import filters
from recipes.paginators import PageLimitPagination
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import status
from .mixins import ListCreateViewSet
from .services import create_shopping_list
from rest_framework.decorators import action
from djoser.views import UserViewSet
from rest_framework.permissions import IsAuthenticated
from .filters import IngredientSearchFilter, CustomRecipesSearchFilter
from django_filters import rest_framework
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from foodgram.settings import PPP
User = get_user_model()


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = PageLimitPagination
    filter_backends = (rest_framework.DjangoFilterBackend, )
    filterset_class = CustomRecipesSearchFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        recipes = Recipe.objects.prefetch_related(
            'ingredient_recipe__ingredient', 'tags').all()
        return recipes

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)

        if request.method == 'POST':
            shopping_list, created = Shopping_list.objects.get_or_create(
                user=user, recipe=recipe)
            shopping_serializer = RecipeFavoriteaAndShoppingSerializer(recipe)
            if created:
                return Response(
                    shopping_serializer.data, status=status.HTTP_201_CREATED)
        try:
            shopping_list = Shopping_list.objects.get(
                user=user, recipe=recipe)
            shopping_list.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Shopping_list.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'],
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        user = request.user
        ingredients = IngredientRecipe.objects.filter(
            recipe__shopping_lists__user=user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).order_by('ingredient__name').annotate(amount=Sum('amount'))
        return create_shopping_list(request, ingredients)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, pk):
        user = request.user
        favorite_recipe = get_object_or_404(Recipe, pk=pk)

        if request.method == 'POST':
            favorite, created = Favorite.objects.get_or_create(
                user=user, favorite=favorite_recipe)
            favorite_serializer = RecipeFavoriteaAndShoppingSerializer(
                favorite_recipe)
            return Response(favorite_serializer.data,
                            status=status.HTTP_201_CREATED)
        try:
            favorite = Favorite.objects.get(
                user=user, favorite=favorite_recipe)
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Favorite.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def get_serializer_class(self):
        if self.request.method in PPP:
            return RecipeCreateSerializer
        return RecipeSerializer


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (filters.SearchFilter, IngredientSearchFilter)
    search_fields = ('=name', 'name')


class FollowViewSet(ListCreateViewSet):
    serializer_class = FollowSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('=following__username', '=user__username',)
    pagination_class = PageLimitPagination

    def get_queryset(self):
        queryset = Follow.objects.filter(user=self.request.user)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class FavoriteViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('=favorite__name', '=user__username',)
    pagination_class = PageLimitPagination

    def get_queryset(self):
        new_queryset = Favorite.objects.filter(user=self.request.user)
        return new_queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (filters.SearchFilter,)
    pagination_class = PageLimitPagination

    @action(
        detail=False, methods=['get', 'patch'],
        url_path='me', url_name='me',
        permission_classes=(IsAuthenticated,)
    )
    def about_me(self, request):
        serializer = UserSerializer(request.user, context={'request': request})
        if request.method == 'PATCH':
            serializer = UserSerializer(
                request.user, data=request.data, partial=True,
                context={'request': request})
            serializer.is_valid(raise_exception=True,
                                context={'request': request})
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,))
    def subscribe(self, request, **kwargs):
        follow_following = get_object_or_404(
            User, id=self.kwargs['id'])
        user = self.request.user
        if request.method == 'POST':
            follow_obj, created = Follow.objects.get_or_create(
                user=user, following=follow_following)
            user_serializer = UserSerializer(
                user, context={'request': request})
            return Response(
                user_serializer.data, status=status.HTTP_201_CREATED)
        try:
            follow_obj = Follow.objects.get(
                user=user, following=follow_following)
            follow_obj.delete()
            user_serializer = UserSerializer(
                user, context={'request': request})
            return Response(
                user_serializer.data, status=status.HTTP_204_NO_CONTENT)
        except Follow.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        queryset = User.objects.filter(following__user=request.user)
        serializer = SubscriptionSerializer(
            self.paginate_queryset(queryset),
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)
