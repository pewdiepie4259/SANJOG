from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from .services import AuthService

User = get_user_model()

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
