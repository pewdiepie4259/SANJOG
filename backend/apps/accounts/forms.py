from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import AdminUserCreationForm, UserChangeForm
from .services import AuthService

User = get_user_model()


class CustomUserCreationForm(AdminUserCreationForm):
    """
    Custom user creation form for Django Admin with role selection and privilege protection.
    """
    class Meta(AdminUserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'role', 'phone_number', 'first_name', 'last_name')

    def __init__(self, *args, current_user=None, **kwargs):
        self.current_user = current_user
        super().__init__(*args, **kwargs)
        if not self.current_user or not self.current_user.is_superuser:
            if 'role' in self.fields:
                self.fields['role'].choices = [
                    (r, l) for r, l in User.RoleChoices.choices if r != User.RoleChoices.ADMIN
                ]
            if 'is_superuser' in self.fields:
                self.fields['is_superuser'].disabled = True
            if 'is_staff' in self.fields:
                self.fields['is_staff'].disabled = True

    def clean_role(self):
        role = self.cleaned_data.get('role')
        if role == User.RoleChoices.ADMIN:
            if not self.current_user or not self.current_user.is_superuser:
                raise ValidationError("Only superusers are authorized to assign the Platform Administrator (ADMIN) role.")
        return role

    def clean(self):
        cleaned_data = super().clean()
        if not self.current_user or not self.current_user.is_superuser:
            cleaned_data['is_superuser'] = False
            cleaned_data.pop('groups', None)
            cleaned_data.pop('user_permissions', None)
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        if not self.current_user or not self.current_user.is_superuser:
            user.is_superuser = False
            if user.role == User.RoleChoices.ADMIN:
                user.role = User.RoleChoices.DONOR
        if commit:
            user.save()
            self.save_m2m()
        return user


class CustomUserChangeForm(UserChangeForm):
    """
    Custom user change form for Django Admin with role protection and M2M privilege defense.
    """
    class Meta(UserChangeForm.Meta):
        model = User
        fields = '__all__'

    def __init__(self, *args, current_user=None, **kwargs):
        self.current_user = current_user
        super().__init__(*args, **kwargs)
        if not self.current_user or not self.current_user.is_superuser:
            if 'role' in self.fields:
                if self.instance and self.instance.role == User.RoleChoices.ADMIN:
                    self.fields['role'].disabled = True
                else:
                    self.fields['role'].choices = [
                        (r, l) for r, l in User.RoleChoices.choices if r != User.RoleChoices.ADMIN
                    ]
            for priv_field in ['is_superuser', 'is_staff', 'groups', 'user_permissions']:
                if priv_field in self.fields:
                    self.fields[priv_field].disabled = True

    def clean_role(self):
        role = self.cleaned_data.get('role')
        if not self.current_user or not self.current_user.is_superuser:
            if role == User.RoleChoices.ADMIN and (not self.instance or self.instance.role != User.RoleChoices.ADMIN):
                raise ValidationError("Only superusers are authorized to assign the Platform Administrator (ADMIN) role.")
            if self.instance and self.instance.role == User.RoleChoices.ADMIN:
                return self.instance.role
        return role

    def clean(self):
        cleaned_data = super().clean()
        if not self.current_user or not self.current_user.is_superuser:
            if self.instance and self.instance.pk:
                cleaned_data['is_superuser'] = self.instance.is_superuser
                cleaned_data['is_staff'] = self.instance.is_staff
                if self.instance.role == User.RoleChoices.ADMIN:
                    cleaned_data['role'] = User.RoleChoices.ADMIN
            else:
                cleaned_data['is_superuser'] = False
        return cleaned_data

    def _save_m2m(self):
        if not self.current_user or not self.current_user.is_superuser:
            self.cleaned_data.pop('groups', None)
            self.cleaned_data.pop('user_permissions', None)
        return super()._save_m2m()


class SANJOGUserRegistrationForm(forms.ModelForm):
    """HTML registration form for Donors, Receivers, and Volunteers."""
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-primary-500 focus:border-transparent text-sm',
            'placeholder': 'Minimum 8 characters'
        }),
        min_length=8,
        label='Password'
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-primary-500 focus:border-transparent text-sm',
            'placeholder': 'Re-enter password'
        }),
        label='Confirm Password'
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'role', 'phone_number', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-primary-500 text-sm',
                'placeholder': 'Choose username'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-primary-500 text-sm',
                'placeholder': 'org@example.com'
            }),
            'role': forms.Select(
                choices=[
                    (User.RoleChoices.DONOR, 'Food Donor (Restaurant / Hotel / Mess)'),
                    (User.RoleChoices.RECEIVER, 'Food Receiver (NGO / Shelter / Kitchen)'),
                    (User.RoleChoices.VOLUNTEER, 'Rescue Volunteer'),
                ],
                attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-primary-500 text-sm bg-white'}
            ),
            'phone_number': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-primary-500 text-sm',
                'placeholder': '+91 9876543210'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-primary-500 text-sm',
                'placeholder': 'First Name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-primary-500 text-sm',
                'placeholder': 'Last Name'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            raise ValidationError({'password_confirm': 'Passwords do not match.'})
        return cleaned_data

    def save(self, commit=True):
        return AuthService.register_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password'],
            role=self.cleaned_data['role'],
            phone_number=self.cleaned_data.get('phone_number'),
            first_name=self.cleaned_data.get('first_name', ''),
            last_name=self.cleaned_data.get('last_name', '')
        )


class SANJOGLoginForm(forms.Form):
    """HTML login form supporting email or username."""
    username_or_email = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-primary-500 text-sm',
            'placeholder': 'Email address or username',
            'autocomplete': 'username'
        }),
        label='Username or Email'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-primary-500 text-sm',
            'placeholder': 'Password',
            'autocomplete': 'current-password'
        }),
        label='Password'
    )
