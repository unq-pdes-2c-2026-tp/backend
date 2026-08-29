from rest_framework.permissions import BasePermission

from users.constants import UserType


class EndUserPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.user_type == UserType.END_USER

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request=request, view=view)


class AgencyPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.user_type == UserType.AGENCY

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request=request, view=view)


class AdminPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.user_type == UserType.ADMIN

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request=request, view=view)
