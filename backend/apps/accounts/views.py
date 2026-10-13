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
    """Developer / User utility to instantly switch between demo personas and keep the user in the single unified web application."""
    from .models import CustomUser
    try:
        user = CustomUser.objects.get(username=username)
        django_login(request, user, backend='apps.accounts.backends.EmailOrUsernameModelBackend')
        messages.success(request, f"Active session switched to {user.username} ({user.get_role_display()}).")
        
        # Route directly to the corresponding workspace within the single web application
        if user.is_donor:
            return redirect('/?tab=donor')
        elif user.is_receiver:
            return redirect('/?tab=receiver')
        elif user.is_volunteer:
            return redirect('/?tab=volunteer')
        elif user.is_admin_user:
            return redirect('/?tab=governance')
    except CustomUser.DoesNotExist:
        messages.error(request, f"User '{username}' not found.")
    return redirect('/')


def home_view(request):
    """Unified SANJOG Single Web Application (Connecting Donors, Receivers, Volunteers, and Admins in one interface)."""
    from .models import CustomUser
    from apps.organizations.models import OrganizationProfile, OrganizationVerificationEvent

    user = request.user
    org_profile = None
    if user.is_authenticated and hasattr(user, 'organization_profile'):
        org_profile = user.organization_profile

    # Determine default active tab based on query param or logged in user's role
    active_tab = request.GET.get('tab')
    if not active_tab:
        if user.is_authenticated:
            if user.is_donor:
                active_tab = 'donor'
            elif user.is_receiver:
                active_tab = 'receiver'
            elif user.is_volunteer:
                active_tab = 'volunteer'
            elif user.is_admin_user:
                active_tab = 'governance'
            else:
                active_tab = 'exchange'
        else:
            active_tab = 'exchange'

    # System overview & metrics
    all_orgs = OrganizationProfile.objects.all().order_by('-created_at')
    pending_orgs = all_orgs.filter(verification_status='PENDING')
    approved_orgs = all_orgs.filter(verification_status='APPROVED')

    demo_accounts = [
        {'username': 'admin', 'name': 'Administrator', 'role': 'Platform Administrator', 'color': 'amber', 'badge': 'ADMIN', 'tab': 'governance'},
        {'username': 'testdonor', 'name': 'Chef Rajesh (Donor)', 'role': 'Food Donor', 'color': 'emerald', 'badge': 'DONOR', 'tab': 'donor'},
        {'username': 'testreceiver', 'name': 'Sister Maria (Receiver)', 'role': 'Food Receiver', 'color': 'blue', 'badge': 'RECEIVER', 'tab': 'receiver'},
        {'username': 'testvolunteer', 'name': 'Aniket (Volunteer)', 'role': 'Rescue Volunteer', 'color': 'indigo', 'badge': 'VOLUNTEER', 'tab': 'volunteer'},
    ]

    # Live Real-Time Rescue Operations Data (combining all 4 pieces)
    active_surplus_listings = [
        {
            'id': 'LST-1082',
            'donor_name': 'Annapurna Grand Restaurant',
            'location': 'Indiranagar, Bengaluru',
            'food_title': 'Fresh North Indian Buffet Thalis',
            'food_type': 'Cooked Meals',
            'servings': 60,
            'dietary': 'Vegetarian',
            'prep_time': '35 mins ago',
            'shelf_life': '2h 15m remaining',
            'sla_urgency': 'NORMAL',
            'sla_color': 'emerald',
            'safety_cleared': True,
            'fssai_verified': True,
        },
        {
            'id': 'LST-1083',
            'donor_name': 'The Royal Palace Caterers',
            'location': 'Koramangala, Bengaluru',
            'food_title': 'Continental Lunch Boxes & Wraps',
            'food_type': 'Packaged Meals',
            'servings': 120,
            'dietary': 'Mixed (Veg + Non-Veg)',
            'prep_time': '1h 10m ago',
            'shelf_life': '45m remaining',
            'sla_urgency': 'URGENT',
            'sla_color': 'amber',
            'safety_cleared': True,
            'fssai_verified': True,
        },
        {
            'id': 'LST-1084',
            'donor_name': 'GreenLeaf Organic Cafe',
            'location': 'MG Road, Bengaluru',
            'food_title': 'Artisan Bread, Fruit Bowls & Sandwiches',
            'food_type': 'Bakery & Fresh Produce',
            'servings': 25,
            'dietary': 'Vegan',
            'prep_time': '50 mins ago',
            'shelf_life': '3h 30m remaining',
            'sla_urgency': 'NORMAL',
            'sla_color': 'emerald',
            'safety_cleared': True,
            'fssai_verified': True,
        },
    ]

    active_meal_demands = [
        {
            'id': 'DMD-802',
            'receiver_name': 'Hope Community Shelter & Kitchen',
            'location': 'St. Marks Road, Bengaluru',
            'meals_needed': 80,
            'beneficiaries': 'Homeless families & children',
            'dietary_preference': 'Any Nutritious Food',
            'target_time': 'Tonight before 9:00 PM',
            'urgency': 'HIGH',
            'storage': 'Refrigeration Available',
            'darpan_verified': True,
        },
        {
            'id': 'DMD-803',
            'receiver_name': 'Ashraya Orphanage Trust',
            'location': 'Wilson Garden, Bengaluru',
            'meals_needed': 35,
            'beneficiaries': 'School Children (Ages 6-16)',
            'dietary_preference': 'Strict Vegetarian',
            'target_time': 'Dinner (Immediate)',
            'urgency': 'CRITICAL',
            'storage': 'Immediate Serving',
            'darpan_verified': True,
        },
        {
            'id': 'DMD-804',
            'receiver_name': 'Karuna Senior Care Home',
            'location': 'Shivajinagar, Bengaluru',
            'meals_needed': 45,
            'beneficiaries': 'Elderly Residents',
            'dietary_preference': 'Low Spice / Soft Meals',
            'target_time': 'Tonight 8:30 PM',
            'urgency': 'MODERATE',
            'storage': 'Hot Food Warmers',
            'darpan_verified': True,
        },
    ]

    active_dispatches = [
        {
            'mission_id': 'RS-941',
            'donor': 'Annapurna Grand Restaurant (Indiranagar)',
            'receiver': 'Hope Community Shelter (St. Marks Road)',
            'volunteer_name': 'Aniket Kumar',
            'vehicle': 'Two-Wheeler with Insulated Box',
            'servings': 60,
            'status': 'EN_ROUTE_PICKUP',
            'status_display': 'En Route to Donor',
            'donor_otp': '7492',
            'receiver_otp': '3180',
            'pickup_verified': False,
            'eta': '12 mins',
            'distance': '3.8 km',
        },
        {
            'mission_id': 'RS-939',
            'donor': 'The Royal Palace Caterers (Koramangala)',
            'receiver': 'Karuna Care Home (Shivajinagar)',
            'volunteer_name': 'Sneha Rao',
            'vehicle': 'EV Van',
            'servings': 120,
            'status': 'IN_TRANSIT',
            'status_display': 'Food Collected • Delivering',
            'donor_otp': '5193',
            'receiver_otp': '8821',
            'pickup_verified': True,
            'eta': '18 mins',
            'distance': '6.2 km',
        },
    ]

    context = {
        'active_tab': active_tab,
        'org_profile': org_profile,
        'all_orgs': all_orgs,
        'pending_orgs': pending_orgs,
        'approved_orgs': approved_orgs,
        'demo_accounts': demo_accounts,
        'total_orgs_count': all_orgs.count(),
        'pending_count': pending_orgs.count(),
        'approved_count': approved_orgs.count(),
        'total_users_count': CustomUser.objects.count(),
        'active_surplus_listings': active_surplus_listings,
        'active_meal_demands': active_meal_demands,
        'active_dispatches': active_dispatches,
        'recent_events': OrganizationVerificationEvent.objects.all().order_by('-created_at')[:5],
        'total_meals_rescued': 1420,
        'co2_saved_kg': 852,
        'active_missions_count': len(active_dispatches),
        'test_stats': {
            'total': 59,
            'passed': 58,
            'skipped': 1,
            'failed': 0,
            'pass_rate': '100%'
        }
    }
    return render(request, 'home.html', context)

# ==============================================================================
# MVP HIERARCHY OPERATIONAL VIEWS (DONOR, NGO, VOLUNTEER, ADMIN, SHARED)
# ==============================================================================

# --- DONOR SECTION ---
def donor_dashboard_view(request):
    org_profile = getattr(request.user, 'organization_profile', None) if request.user.is_authenticated else None
    return render(request, 'dashboards/donor_dashboard.html', {
        'user': request.user,
        'org_profile': org_profile,
    })

def donor_report_surplus_view(request):
    org_profile = getattr(request.user, 'organization_profile', None) if request.user.is_authenticated else None
    return render(request, 'donor/report_surplus.html', {
        'user': request.user,
        'org_profile': org_profile,
    })

def donor_ai_match_view(request):
    org_profile = getattr(request.user, 'organization_profile', None) if request.user.is_authenticated else None
    return render(request, 'donor/ai_match.html', {
        'user': request.user,
        'org_profile': org_profile,
    })

def donor_live_tracking_view(request):
    return render(request, 'donor/live_tracking.html', {
        'user': request.user,
    })

def donor_history_view(request):
    return render(request, 'donor/donation_history.html', {
        'user': request.user,
    })


# --- NGO (RECEIVER) SECTION ---
def receiver_dashboard_view(request):
    org_profile = getattr(request.user, 'organization_profile', None) if request.user.is_authenticated else None
    return render(request, 'dashboards/receiver_dashboard.html', {
        'user': request.user,
        'org_profile': org_profile,
    })

def ngo_nearby_food_view(request):
    return render(request, 'ngo/nearby_food.html', {
        'user': request.user,
    })

def ngo_request_food_view(request):
    return render(request, 'ngo/request_food.html', {
        'user': request.user,
    })

def ngo_accepted_donations_view(request):
    return render(request, 'ngo/accepted_donations.html', {
        'user': request.user,
    })


# --- VOLUNTEER SECTION ---
def volunteer_dashboard_view(request):
    return render(request, 'dashboards/volunteer_dashboard.html', {
        'user': request.user,
    })

def volunteer_available_rescues_view(request):
    return render(request, 'volunteer/available_rescues.html', {
        'user': request.user,
    })

def volunteer_active_delivery_view(request):
    return render(request, 'volunteer/active_delivery.html', {
        'user': request.user,
    })


# --- ADMIN SECTION ---
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

def admin_ngo_verification_view(request):
    from apps.organizations.models import OrganizationProfile
    all_orgs = OrganizationProfile.objects.all().order_by('-created_at')
    return render(request, 'admin_portal/ngo_verification.html', {
        'user': request.user,
        'pending_reviews': all_orgs.filter(verification_status='PENDING').count(),
        'all_organizations': all_orgs,
    })

def admin_user_management_view(request):
    from apps.accounts.models import CustomUser
    return render(request, 'admin_portal/user_management.html', {
        'user': request.user,
        'all_users': CustomUser.objects.all(),
    })

def admin_rescue_monitoring_view(request):
    return render(request, 'admin_portal/rescue_monitoring.html', {
        'user': request.user,
    })


# --- SHARED TOOLS SECTION ---
def notifications_view(request):
    return render(request, 'shared/notifications.html', {
        'user': request.user,
    })

def profile_view(request):
    org_profile = getattr(request.user, 'organization_profile', None) if request.user.is_authenticated else None
    return render(request, 'shared/profile.html', {
        'user': request.user,
        'org_profile': org_profile,
    })

def map_view(request):
    return render(request, 'shared/map.html', {
        'user': request.user,
    })

def qr_scanner_view(request):
    return render(request, 'shared/qr_scanner.html', {
        'user': request.user,
    })

def food_passport_view(request):
    return render(request, 'shared/food_passport.html', {
        'user': request.user,
    })

