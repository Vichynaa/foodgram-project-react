from django.urls import include, path
from rest_framework.routers import DefaultRouter
from . views import RecipeViewSet, FollowViewSet

router_v1 = DefaultRouter()
router_v1.register('recipes', RecipeViewSet)
# router_v1.register('groups', GroupViewSet)
router_v1.register(
    'follow', FollowViewSet,
    basename='follow'
)

urlpatterns = [
    path('v1/', include('djoser.urls')),
    path('v1/', include('djoser.urls.jwt')),
    path('v1/', include(router_v1.urls))
]