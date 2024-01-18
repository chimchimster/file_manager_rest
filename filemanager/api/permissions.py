from rest_framework.permissions import BasePermission


class AllowUploadPermission(BasePermission):
    def has_permission(self, request, view):

        return request.method == 'PUT'


class AllowDeletePermission(BasePermission):

    def has_permission(self, request, view):

        return request.method == 'DELETE'


__all__ = ('AllowUploadPermission', 'AllowDeletePermission')