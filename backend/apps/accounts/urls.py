from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from . import api_views

urlpatterns = [
    # Template Auth Routes
    path('', views.home_view, name='home'),
    path('quick-switch/<str:username>/', views.quick_switch_view, name='quick_switch'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('api/v1/login/', views.LoginView.as_view()),
    path('logout/', views.LogoutView.as_view(), name='logout'),

    # Role Dashboard & MVP Hierarchy Routes
    # --- Donor Routes ---
    path('donor/dashboard/', views.donor_dashboard_view, name='donor_dashboard'),
    path('donor/report-surplus/', views.donor_report_surplus_view, name='donor_report_surplus'),
    path('donor/ai-match/', views.donor_ai_match_view, name='donor_ai_match'),
    path('donor/live-tracking/', views.donor_live_tracking_view, name='donor_live_tracking'),
    path('donor/history/', views.donor_history_view, name='donor_history'),

    # --- NGO (Receiver) Routes ---
    path('receiver/dashboard/', views.receiver_dashboard_view, name='receiver_dashboard'),
    path('ngo/dashboard/', views.receiver_dashboard_view, name='ngo_dashboard'),
    path('ngo/nearby-food/', views.ngo_nearby_food_view, name='ngo_nearby_food'),
    path('ngo/request-food/', views.ngo_request_food_view, name='ngo_request_food'),
    path('ngo/accepted-donations/', views.ngo_accepted_donations_view, name='ngo_accepted_donations'),

    # --- Volunteer Routes ---
    path('volunteer/dashboard/', views.volunteer_dashboard_view, name='volunteer_dashboard'),
    path('volunteer/available-rescues/', views.volunteer_available_rescues_view, name='volunteer_available_rescues'),
    path('volunteer/active-delivery/', views.volunteer_active_delivery_view, name='volunteer_active_delivery'),

    # --- Admin Routes ---
    path('platform-admin/dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    path('platform-admin/ngo-verification/', views.admin_ngo_verification_view, name='admin_ngo_verification'),
    path('platform-admin/user-management/', views.admin_user_management_view, name='admin_user_management'),
    path('platform-admin/rescue-monitoring/', views.admin_rescue_monitoring_view, name='admin_rescue_monitoring'),

    # --- Shared Tools Routes ---
    path('notifications/', views.notifications_view, name='notifications'),
    path('profile/', views.profile_view, name='profile'),
    path('map/', views.map_view, name='map'),
    path('qr-scanner/', views.qr_scanner_view, name='qr_scanner'),
    path('food-passport/', views.food_passport_view, name='food_passport'),

    # Built-in Password Reset Views
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='accounts/password_reset.html',
        email_template_name='accounts/password_reset_email.html',
        subject_template_name='accounts/password_reset_subject.txt',
        success_url='/password-reset/done/'
    ), name='password_reset'),
    
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='accounts/password_reset_done.html'
    ), name='password_reset_done'),

    path('password-reset/confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='accounts/password_reset_confirm.html',
        success_url='/password-reset/complete/'
    ), name='password_reset_confirm'),

    path('password-reset/complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/password_reset_complete.html'
    ), name='password_reset_complete'),

    # REST API Auth Endpoints (/api/v1/auth/)
    path('api/v1/auth/register/', api_views.APIRegisterView.as_view(), name='api_auth_register'),
    path('api/v1/auth/login/', api_views.APILoginView.as_view(), name='api_auth_login'),
    path('api/v1/auth/logout/', api_views.APILogoutView.as_view(), name='api_auth_logout'),
    path('api/v1/auth/me/', api_views.APIUserProfileView.as_view(), name='api_auth_me'),
]
