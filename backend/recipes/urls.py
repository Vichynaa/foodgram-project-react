from recipes.views import (
    IngredientViewSet,
    RecipeViewSet,
    TagViewSet,
    UserViewSet,
    FollowViewSet,
    FavoriteViewSet,
    ShoppinglistViewSet
)
from django.urls import include, path
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("tags", TagViewSet, "tags")
router.register("ingredients", IngredientViewSet, "ingredients")
router.register("recipes", RecipeViewSet, "recipes")
router.register("users", UserViewSet, "users")
router.register("follow", FollowViewSet, "follow")
router.register("favorite", FavoriteViewSet, "favorite")
router.register("carts", ShoppinglistViewSet, "carts")

urlpatterns = (
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    path("", include(router.urls)),
)
