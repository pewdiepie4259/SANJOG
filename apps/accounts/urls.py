from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from . import api_views

urlpatterns = [
    # Template Auth Routes
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),

    # Role Dashboard Placeholder Routes
    path('donor/dashboard/', views.donor_dashboard_view, name='donor_dashboard'),
    path('receiver/dashboard/', views.receiver_dashboard_view, name='receiver_dashboard'),
    path('volunteer/dashboard/', views.volunteer_dashboard_view, name='volunteer_dashboard'),
    path('platform-admin/dashboard/', views.admin_dashboard_view, name='admin_dashboard'),

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
