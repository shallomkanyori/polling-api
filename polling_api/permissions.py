from rest_framework import permissions

class IsPollCreatorOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow the creator of a poll to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the creator of the poll.
        return obj.created_by == request.user or request.user.is_staff

class IsSelfOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow users to edit themselves.
    """
    def has_object_permission(self, request, view, obj):
        return obj == request.user or request.user.is_staff