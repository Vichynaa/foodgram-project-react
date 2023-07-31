from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """
    def has_object_permission(self, request, view, obj):
        return request.method in permissions.SAFE_METHODS or \
            obj.author == request.user


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_anonymous:
            return (
                request.user.is_superuser
            )
        return (
            request.method in SAFE_METHODS
            or (request.user.is_authenticated)
        )
