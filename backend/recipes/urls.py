from recipes.views import (
    IngredientViewSet,
    RecipeViewSet,
    TagViewSet,
    CustomUserViewSet
)
from django.urls import include, path
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register("tags", TagViewSet, "tags")
router.register("ingredients", IngredientViewSet, "ingredients")
router.register("recipes", RecipeViewSet, "recipes")
router.register("users", CustomUserViewSet, "users")

urlpatterns = (
    path("auth/", include("djoser.urls.authtoken")),
    path("", include(router.urls)),
)
