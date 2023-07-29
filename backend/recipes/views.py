from rest_framework import viewsets
from .models import Recipe, Tag, Ingredient, Follow, Favorite
from .serializers import RecipeSerializer, TagSerializer, IngredientSerializer
from .serializers import FollowSerializer, FavoriteSerializer
from rest_framework import mixins
from rest_framework import permissions
from rest_framework.pagination import LimitOffsetPagination
from rest_framework import filters
from .permissions import IsAdminOrReadOnly
from recipes.paginators import PageLimitPagination
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Q
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.permissions import DjangoModelPermissions
from rest_framework import status
from django.shortcuts import get_object_or_404
User = get_user_model()


class ListCreateViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    pass


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = PageLimitPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        recipes = Recipe.objects.prefetch_related(
            'rname_recipe_ingredients__ingredient', 'tags')
        return recipes

    @action(methods=['post', 'delete'],
            detail=True, url_path='favorite', url_name='favorite')
    def favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = self.request.user
        if request.method == 'POST':
            if Favorite.objects.filter(user=user, recipe=recipe).exists():
                return Response({"errors": "Уже создан"},
                                status=status.HTTP_400_BAD_REQUEST)
            favorite = Favorite.objects.create(user=user, recipe=recipe)
            recipe = favorite.recipe
            serialised_data = FavoriteSerializer(instance=recipe)
            return Response(serialised_data.data,
                            status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            if not Favorite.objects.filter(user=user, recipe=recipe).exists():
                return Response({"errors": "Удалён"},
                                status=status.HTTP_400_BAD_REQUEST)
            favorite = Favorite.objects.get(user=user, recipe=recipe)
            favorite.delete()
            return Response(None)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = [IsAdminOrReadOnly]


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = IsAdminOrReadOnly


class FollowViewSet(ListCreateViewSet):
    serializer_class = FollowSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('following__username', 'user__username',)
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        new_queryset = Follow.objects.filter(user=self.request.user)
        return new_queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class FavoriteViewSet(ListCreateViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('favorite__name', 'user__username',)
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        new_queryset = Favorite.objects.filter(user=self.request.user)
        return new_queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UserViewSet(viewsets.ModelViewSet):
    pagination_class = PageLimitPagination
    permission_classes = (DjangoModelPermissions,)
    add_serializer = FollowSerializer
    link_model = Follow

    @action(detail=True, permission_classes=(IsAuthenticated,))
    def subscribe(self, request: WSGIRequest, id: int | str) -> Response:
        """..."""

    @subscribe.mapping.post
    def create_subscribe(
        self, request: WSGIRequest, id: int | str
    ) -> Response:
        return self._create_relation(id)

    @subscribe.mapping.delete
    def delete_subscribe(
        self, request: WSGIRequest, id: int | str
    ) -> Response:
        return self._delete_relation(Q(author__id=id))

    @action(
        methods=("get",), detail=False, permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request: WSGIRequest) -> Response:
        pages = self.paginate_queryset(
            User.objects.filter(subscribers__user=self.request.user)
        )
        serializer = FollowSerializer(pages, many=True)
        return self.get_paginated_response(serializer.data)
