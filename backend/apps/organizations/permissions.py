from rest_framework import permissions

class IsOrganizationOwner(permissions.BasePermission):
    """
    Allows access only to the user who owns the organization profile or document.
    """
    def has_object_permission(self, request, view, obj):
        if not (request.user and request.user.is_authenticated):
            return False

        # Support OrganizationProfile or OrganizationDocument
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'organization'):
            return obj.organization.user == request.user
        return False


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Allows access to organization owner or platform administrators.
    """
    def has_object_permission(self, request, view, obj):
        if not (request.user and request.user.is_authenticated):
            return False

        if request.user.is_admin_user:
            return True

        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'organization'):
            return obj.organization.user == request.user
        return False


class IsVerifiedOrganization(permissions.BasePermission):
    """
    Allows access only to authenticated users with an APPROVED/verified organization profile.
    Used by downstream modules (Food Listings, Demand Requests).
    """
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            hasattr(request.user, 'organization_profile') and
            request.user.organization_profile.is_verified
        )
