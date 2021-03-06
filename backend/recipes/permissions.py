from rest_framework import permissions
from rest_framework.permissions import (BasePermission,
                                        IsAuthenticatedOrReadOnly)


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_authenticated:
            return request.user.is_staff or request.user.is_admin
        return False


class IsAuthorOrAdminOrReadOnly(IsAuthenticatedOrReadOnly):

    def has_object_permission(self, request, view, obj):

        if request.method in permissions.SAFE_METHODS:
            return True

        return (obj.author == request.user
                or request.user.is_authenticated
                and request.user.is_superuser)
