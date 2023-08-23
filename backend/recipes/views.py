from rest_framework import viewsets
from .models import Recipe, Tag, Ingredient, Follow, Favorite, Shopping_list
from .models import IngredientRecipe
from .serializers import RecipeSerializer, TagSerializer, IngredientSerializer
from .serializers import FollowSerializer, FavoriteSerializer, UserSerializer
from .serializers import AdminUserSerializer
from .serializers import RecipeCreateSerializer
from rest_framework import permissions
from rest_framework import filters
from .permissions import IsAdminOrReadOnly
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
User = get_user_model()


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = PageLimitPagination
    filter_backends = (rest_framework.DjangoFilterBackend,)
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
            if created:
                return Response(status=status.HTTP_201_CREATED)
            else:
                return Response(status=status.HTTP_200_OK)
        elif request.method == 'DELETE':
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
        return create_shopping_list(self, request, ingredients)

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'update':
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
    serializer_class = AdminUserSerializer
    permission_classes = (IsAuthenticated, IsAdminOrReadOnly)
    filter_backends = (filters.SearchFilter,)
    lookup_field = 'username'
    lookup_value_regex = r'[\w\@\.\+\-]+'
    search_fields = ('username',)

    @action(
        detail=False, methods=['get', 'patch'],
        url_path='me', url_name='me',
        permission_classes=(IsAuthenticated,)
    )
    def about_me(self, request):
        serializer = UserSerializer(request.user)
        if request.method == 'PATCH':
            serializer = UserSerializer(
                request.user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.data, status=status.HTTP_200_OK)
