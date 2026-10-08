from functools import wraps
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied

def role_required(allowed_roles=None):
    """
    View decorator enforcing Role-Based Access Control (RBAC).
    Redirects unauthenticated users to login; renders 403 Forbidden page
    for authenticated users attempting cross-role access.
    """
    if allowed_roles is None:
        allowed_roles = []

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.warning(request, "Please sign in to access this operating portal.")
                return redirect(f"/login/?next={request.path}")

            # Check if user role matches allowed roles or is superuser
            if request.user.is_superuser or request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)

            # Block unauthorized cross-role access
            context = {
                'error_title': '403 — Access Forbidden',
                'error_message': f'Access Denied: Your assigned role ({request.user.get_role_display()}) does not have permission to view this operational dashboard.'
            }
            return render(request, '403.html', context, status=403)
        return _wrapped_view
    return decorator


def donor_required(view_func):
    return role_required(['DONOR'])(view_func)

def receiver_required(view_func):
    return role_required(['RECEIVER'])(view_func)

def volunteer_required(view_func):
    return role_required(['VOLUNTEER'])(view_func)

def admin_required(view_func):
    return role_required(['ADMIN'])(view_func)
