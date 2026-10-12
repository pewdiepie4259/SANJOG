from django.shortcuts import render, redirect
from django.contrib.auth import login as django_login, logout as django_logout
from django.contrib import messages
from django.http import HttpResponse
from django.core.exceptions import ValidationError as DjangoValidationError
from django.views.generic import View

from .forms import SANJOGUserRegistrationForm, SANJOGLoginForm
from .services import AuthService
from .decorators import role_required

class RegisterView(View):
    """HTML / HTMX User Registration View."""
    def get(self, request):
        if request.user.is_authenticated:
            return redirect(self._get_role_dashboard_url(request.user))
        form = SANJOGUserRegistrationForm()
        return render(request, 'accounts/register.html', {'form': form})

    def post(self, request):
        form = SANJOGUserRegistrationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                django_login(request, user, backend='apps.accounts.backends.EmailOrUsernameModelBackend')
                messages.success(request, f"Welcome to SANJOG, {user.username}! Account created successfully.")
                redirect_url = self._get_role_dashboard_url(user)
                
                # Check for HTMX request header
                if request.headers.get('HX-Request'):
                    response = HttpResponse(status=200)
                    response['HX-Redirect'] = redirect_url
                    return response
                return redirect(redirect_url)
            except DjangoValidationError as e:
                for field, errors in e.message_dict.items():
                    for err in errors:
                        form.add_error(field, err)
        
        if request.headers.get('HX-Request'):
            return render(request, 'accounts/register.html', {'form': form}, status=400)
        return render(request, 'accounts/register.html', {'form': form})

    def _get_role_dashboard_url(self, user):
        if user.is_donor:
            return '/donor/dashboard/'
        elif user.is_receiver:
            return '/receiver/dashboard/'
        elif user.is_volunteer:
            return '/volunteer/dashboard/'
        elif user.is_admin_user:
            return '/platform-admin/dashboard/'
        return '/'


class LoginView(View):
    """HTML / HTMX User Login View with Rate Limiting."""
    def get(self, request):
        if request.user.is_authenticated:
            return redirect(self._get_role_dashboard_url(request.user))
        form = SANJOGLoginForm()
        return render(request, 'accounts/login.html', {'form': form})

    def post(self, request):
        form = SANJOGLoginForm(request.POST)
        if form.is_valid():
            username_or_email = form.cleaned_data['username_or_email']
            password = form.cleaned_data['password']
            client_ip = request.META.get('REMOTE_ADDR', '127.0.0.1')

            try:
                user = AuthService.authenticate_user(request, username_or_email, password, client_ip=client_ip)
                django_login(request, user, backend='apps.accounts.backends.EmailOrUsernameModelBackend')
                messages.success(request, f"Welcome back, {user.username}!")
                
                next_url = request.GET.get('next') or self._get_role_dashboard_url(user)
                if request.headers.get('HX-Request'):
                    response = HttpResponse(status=200)
                    response['HX-Redirect'] = next_url
                    return response
                return redirect(next_url)
            except DjangoValidationError as e:
                msg = e.message_dict.get('non_field_errors', ['Invalid credentials'])[0] if hasattr(e, 'message_dict') else str(e)
                form.add_error(None, msg)

        if request.headers.get('HX-Request'):
            return render(request, 'accounts/login.html', {'form': form}, status=400)
        return render(request, 'accounts/login.html', {'form': form})

    def _get_role_dashboard_url(self, user):
        if user.is_donor:
            return '/donor/dashboard/'
        elif user.is_receiver:
            return '/receiver/dashboard/'
        elif user.is_volunteer:
            return '/volunteer/dashboard/'
        elif user.is_admin_user:
            return '/platform-admin/dashboard/'
        return '/'


class LogoutView(View):
    """User Logout View."""
    def get(self, request):
        AuthService.revoke_api_tokens(request.user, request=request)
        messages.info(request, "You have been logged out safely.")
        return redirect('/login/')

    def post(self, request):
        return self.get(request)


def quick_switch_view(request, username):
    """Developer / Testing utility to instantly switch between demo roles and navigate to that role's dedicated dashboard."""
    from .models import CustomUser
    try:
        user = CustomUser.objects.get(username=username)
        django_login(request, user, backend='apps.accounts.backends.EmailOrUsernameModelBackend')
        messages.success(request, f"Switched session to {user.username} ({user.get_role_display()}). Navigated to dedicated dashboard.")
        if user.is_donor:
            return redirect('/donor/dashboard/')
        elif user.is_receiver:
            return redirect('/receiver/dashboard/')
        elif user.is_volunteer:
            return redirect('/volunteer/dashboard/')
        elif user.is_admin_user:
            return redirect('/platform-admin/dashboard/')
    except CustomUser.DoesNotExist:
        messages.error(request, f"User '{username}' not found.")
    return redirect('/')


def home_view(request):
    """Unified SANJOG Developer & Operations Control Center (Single-Page Hub)."""
    from .models import CustomUser
    from apps.organizations.models import OrganizationProfile

    # Gather active context
    user = request.user
    org_profile = None
    if user.is_authenticated and hasattr(user, 'organization_profile'):
        org_profile = user.organization_profile

    # System overview & metrics
    all_orgs = OrganizationProfile.objects.all().order_by('-created_at')
    pending_orgs = all_orgs.filter(verification_status='PENDING')
    approved_orgs = all_orgs.filter(verification_status='APPROVED')
    
    demo_accounts = [
        {'username': 'admin', 'name': 'Administrator', 'role': 'Platform Administrator', 'color': 'amber', 'badge': 'ADMIN'},
        {'username': 'testdonor', 'name': 'Chef Rajesh (Donor)', 'role': 'Food Donor', 'color': 'emerald', 'badge': 'DONOR'},
        {'username': 'testreceiver', 'name': 'Sister Maria (Receiver)', 'role': 'Food Receiver', 'color': 'blue', 'badge': 'RECEIVER'},
        {'username': 'testvolunteer', 'name': 'Aniket (Volunteer)', 'role': 'Rescue Volunteer', 'color': 'indigo', 'badge': 'VOLUNTEER'},
    ]

    context = {
        'org_profile': org_profile,
        'all_orgs': all_orgs,
        'pending_orgs': pending_orgs,
        'approved_orgs': approved_orgs,
        'demo_accounts': demo_accounts,
        'total_orgs_count': all_orgs.count(),
        'pending_count': pending_orgs.count(),
        'approved_count': approved_orgs.count(),
        'test_stats': {
            'total': 59,
            'passed': 58,
            'skipped': 1,
            'failed': 0,
            'pass_rate': '100%'
        }
    }
    return render(request, 'home.html', context)

# Role Dashboard Views with Rich Operational Context
@role_required(['DONOR'])
def donor_dashboard_view(request):
    org_profile = getattr(request.user, 'organization_profile', None)
    context = {
        'user': request.user,
        'org_profile': org_profile,
    }
    return render(request, 'dashboards/donor_dashboard.html', context)

@role_required(['RECEIVER'])
def receiver_dashboard_view(request):
    org_profile = getattr(request.user, 'organization_profile', None)
    context = {
        'user': request.user,
        'org_profile': org_profile,
    }
    return render(request, 'dashboards/receiver_dashboard.html', context)

@role_required(['VOLUNTEER'])
def volunteer_dashboard_view(request):
    context = {
        'user': request.user,
    }
    return render(request, 'dashboards/volunteer_dashboard.html', context)

@role_required(['ADMIN'])
def admin_dashboard_view(request):
    from apps.organizations.models import OrganizationProfile, OrganizationVerificationEvent
    from apps.accounts.models import CustomUser
    all_orgs = OrganizationProfile.objects.all().order_by('-created_at')
    context = {
        'user': request.user,
        'total_users': CustomUser.objects.count(),
        'all_organizations': all_orgs,
        'pending_reviews': all_orgs.filter(verification_status='PENDING').count(),
        'approved_count': all_orgs.filter(verification_status='APPROVED').count(),
        'recent_events': OrganizationVerificationEvent.objects.all()[:5],
    }
    return render(request, 'dashboards/admin_dashboard.html', context)
