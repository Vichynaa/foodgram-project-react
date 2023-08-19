from recipes.views import (
    IngredientViewSet,
    RecipeViewSet,
    TagViewSet,
    FollowViewSet,
    FavoriteViewSet,
    ShoppinglistViewSet,
    CustomUserViewSet
)
from django.urls import include, path
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register("tags", TagViewSet, "tags")
router.register("ingredients", IngredientViewSet, "ingredients")
router.register("recipes", RecipeViewSet, "recipes")
router.register("users", CustomUserViewSet, "users")
router.register("follow", FollowViewSet, "follow")
# router.register("favorite", FavoriteViewSet, "favorite")
# router.register("shopping_cart", ShoppinglistViewSet, "shopping_cart")
router.register(r"recipes/(?P<id>\d+)/shopping_cart", ShoppinglistViewSet, "recipe-shopping-cart")
router.register(r"recipes/(?P<id>\d+)/favorite", FavoriteViewSet, "favorite")
urlpatterns = (
    path("auth/", include("djoser.urls.authtoken")),
    path("", include(router.urls)),
)
