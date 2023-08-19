from rest_framework import viewsets
from .models import Recipe, Tag, Ingredient, Follow, Favorite, Shopping_list
from .serializers import RecipeSerializer, TagSerializer, IngredientSerializer
from .serializers import FollowSerializer, FavoriteSerializer, UserSerializer
from .serializers import AdminUserSerializer, ShoppinglistSerializer
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
from .services import create_shoping_list
from rest_framework.decorators import action
from django.http.response import HttpResponse
from djoser.views import UserViewSet
from rest_framework.permissions import IsAuthenticated
from .filters import IngredientSearchFilter, CustomRecipesSearchFilter
from django_filters import rest_framework
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


class ShoppinglistViewSet(viewsets.ModelViewSet):
    serializer_class = ShoppinglistSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('=recipe__name', '=user__username',)
    pagination_class = PageLimitPagination

    def get_queryset(self):
        new_queryset = Shopping_list.objects.filter(user=self.request.user)
        return new_queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def download_shopping_list(self, request):
        user = self.request.user
        if not user.carts.exists():
            return Response(status=status.HTTP_404_NOT_FOUND)

        filename = f'{user.username}_shopping_list.txt'
        shopping_list = create_shoping_list(user)
        response = HttpResponse(
            shopping_list, content_type='text/plain; charset=utf-8'
        )
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = AdminUserSerializer
    permission_classes = (IsAuthenticated, IsAdminOrReadOnly)
    filter_backends = (filters.SearchFilter,)
    lookup_field = 'username'
    lookup_value_regex = r'[\w\@\.\+\-]+'
    search_fields = ('username',)

    def update(self, request, *args, **kwargs):
        if request.method == 'PUT':
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

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
