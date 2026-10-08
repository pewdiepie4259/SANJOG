from rest_framework import permissions

class IsDonor(permissions.BasePermission):
    """Allows REST API access only to authenticated users with DONOR role."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_donor)


class IsReceiver(permissions.BasePermission):
    """Allows REST API access only to authenticated users with RECEIVER role."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_receiver)


class IsVolunteer(permissions.BasePermission):
    """Allows REST API access only to authenticated users with VOLUNTEER role."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_volunteer)


class IsAdminUser(permissions.BasePermission):
    """Allows REST API access only to authenticated platform admins/superusers."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_admin_user)


class IsSelfOrAdmin(permissions.BasePermission):
    """Allows users to read/edit only their own user object unless superuser."""
    def has_object_permission(self, request, view, obj):
        return bool(
            request.user and request.user.is_authenticated and
            (obj == request.user or request.user.is_admin_user)
        )
