from django import forms
from django.core.exceptions import ValidationError
from .models import OrganizationProfile, OrganizationDocument
from .validators import (
    OrganizationType, 
    DocumentType, 
    DONOR_ORG_TYPES, 
    RECEIVER_ORG_TYPES,
    validate_organization_type_for_role,
    validate_file_security
)

class OrganizationProfileForm(forms.ModelForm):
    """HTML / HTMX Form for creating and editing Organization Profiles."""
    
    class Meta:
        model = OrganizationProfile
        fields = [
            'name', 'org_type', 'registration_number',
            'contact_person', 'contact_email', 'contact_phone',
            'address_line1', 'address_line2', 'city', 'state', 'postal_code', 'country',
            'latitude', 'longitude'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-primary-500 text-sm',
                'placeholder': 'Legal Organization / Facility Name'
            }),
            'org_type': forms.Select(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-primary-500 text-sm bg-white'
            }),
            'registration_number': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-primary-500 text-sm',
                'placeholder': 'FSSAI License / 80G / Trust Reg / CIN'
            }),
            'contact_person': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-primary-500 text-sm',
                'placeholder': 'Authorized Representative Name'
            }),
            'contact_email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-primary-500 text-sm',
                'placeholder': 'org@example.com'
            }),
            'contact_phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-primary-500 text-sm',
                'placeholder': '+91 9876543210'
            }),
            'address_line1': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-primary-500 text-sm',
                'placeholder': 'Street Address / Building'
            }),
            'address_line2': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-primary-500 text-sm',
                'placeholder': 'Suite / Floor / Landmark (Optional)'
            }),
            'city': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-primary-500 text-sm',
                'placeholder': 'City'
            }),
            'state': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-primary-500 text-sm',
                'placeholder': 'State / Province'
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-primary-500 text-sm',
                'placeholder': 'PIN / Postal Code'
            }),
            'country': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-primary-500 text-sm',
                'placeholder': 'Country'
            }),
            'latitude': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-primary-500 text-sm',
                'placeholder': 'e.g. 19.076090',
                'step': '0.000001'
            }),
            'longitude': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-primary-500 text-sm',
                'placeholder': 'e.g. 72.877426',
                'step': '0.000001'
            }),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

        # Filter organization type choices based on user role
        if user:
            if user.is_donor:
                self.fields['org_type'].choices = [(c.value, c.label) for c in DONOR_ORG_TYPES]
            elif user.is_receiver:
                self.fields['org_type'].choices = [(c.value, c.label) for c in RECEIVER_ORG_TYPES]

    def clean_org_type(self):
        org_type = self.cleaned_data.get('org_type')
        if self.user:
            validate_organization_type_for_role(self.user.role, org_type)
        return org_type

    def clean_latitude(self):
        lat = self.cleaned_data.get('latitude')
        if lat is not None and (lat < -90 or lat > 90):
            raise ValidationError('Latitude must be between -90 and 90 degrees.')
        return lat

    def clean_longitude(self):
        lon = self.cleaned_data.get('longitude')
        if lon is not None and (lon < -180 or lon > 180):
            raise ValidationError('Longitude must be between -180 and 180 degrees.')
        return lon


class OrganizationDocumentUploadForm(forms.ModelForm):
    """HTML / HTMX Form for uploading verification documents."""

    class Meta:
        model = OrganizationDocument
        fields = ['document_type', 'file']
        widgets = {
            'document_type': forms.Select(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-primary-500 text-sm bg-white'
            }),
            'file': forms.FileInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-primary-500 text-sm bg-white'
            }),
        }

    def clean_file(self):
        uploaded_file = self.cleaned_data.get('file')
        if uploaded_file:
            validate_file_security(uploaded_file)
        return uploaded_file


class AdminOrganizationRejectForm(forms.Form):
    """Form used by admins to reject an organization with mandatory notes."""
    rejection_reason = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full p-3 rounded-xl border border-slate-300 focus:ring-2 focus:ring-red-500 text-sm',
            'rows': 4,
            'placeholder': 'State clearly why verification was rejected (e.g., expired FSSAI license, blurry image, invalid registration number)...'
        }),
        required=True,
        label="Rejection Reason (Required)"
    )


class AdminDocumentReviewForm(forms.Form):
    """Form used by admins to review an individual document."""
    decision = forms.ChoiceField(
        choices=[('APPROVED', 'Approve Document'), ('REJECTED', 'Reject Document')],
        widget=forms.Select(attrs={
            'class': 'px-3 py-1.5 rounded-lg border border-slate-300 text-xs font-semibold'
        })
    )
    rejection_reason = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'px-3 py-1.5 rounded-lg border border-slate-300 text-xs w-full',
            'placeholder': 'Reason if rejected (e.g. illegible certificate)'
        }),
        required=False
    )

    def clean(self):
        cleaned_data = super().clean()
        decision = cleaned_data.get('decision')
        reason = cleaned_data.get('rejection_reason')
        if decision == 'REJECTED' and not reason:
            raise ValidationError({'rejection_reason': 'Rejection reason is required when rejecting a document.'})
        return cleaned_data
