import uuid
from pathlib import Path
from django.db import models
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.exceptions import ValidationError, PermissionDenied
from .validators import OrganizationType, DocumentType, validate_organization_type_for_role

def get_private_document_storage():
    """Returns private FileSystemStorage backend configured outside public media root."""
    return FileSystemStorage(
        location=settings.PRIVATE_MEDIA_ROOT,
        base_url=None  # Explicitly prevents public URL generation
    )

private_document_storage = get_private_document_storage()

def organization_document_upload_path(instance, filename):
    """Generates isolated UUID-based filename on disk to prevent path traversal."""
    ext = Path(filename).suffix.lower()
    return f"org_{instance.organization_id}/{uuid.uuid4()}{ext}"


class OrganizationProfile(models.Model):
    """
    Organization Profile for Food Donors and Receivers.
    Stores operational details, physical location, and verification status.
    """
    class VerificationStatus(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft / Incomplete'
        PENDING = 'PENDING', 'Pending Admin Verification'
        APPROVED = 'APPROVED', 'Verified & Approved'
        REJECTED = 'REJECTED', 'Verification Rejected'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='organization_profile',
        help_text="Primary registered user account managing this organization"
    )
    name = models.CharField(max_length=255, help_text="Official legal or business trade name")
    org_type = models.CharField(max_length=50, choices=OrganizationType.choices)
    registration_number = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        unique=True,
        help_text="FSSAI License / 80G / Society Registration / CIN number"
    )

    # Authorized Contact Information
    contact_person = models.CharField(max_length=150, help_text="Primary authorized contact representative")
    contact_email = models.EmailField(help_text="Operational email for notifications and alerts")
    contact_phone = models.CharField(max_length=20, help_text="Operational phone number")

    # Physical Address
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True, default='')
    city = models.CharField(max_length=100, db_index=True)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default='India')

    # Geolocation Coordinates (Decimal precision 9,6 for ~11cm physical accuracy)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    # Verification State & Latest Decision Cache
    verification_status = models.CharField(
        max_length=20,
        choices=VerificationStatus.choices,
        default=VerificationStatus.DRAFT,
        db_index=True
    )
    rejection_reason = models.TextField(blank=True, default='')
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_organizations'
    )
    verified_at = models.DateTimeField(null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_verified(self):
        return self.verification_status == self.VerificationStatus.APPROVED

    @property
    def is_pending(self):
        return self.verification_status == self.VerificationStatus.PENDING

    @property
    def is_rejected(self):
        return self.verification_status == self.VerificationStatus.REJECTED

    @property
    def is_draft(self):
        return self.verification_status == self.VerificationStatus.DRAFT

    @property
    def location_coords(self):
        if self.latitude is not None and self.longitude is not None:
            return (float(self.latitude), float(self.longitude))
        return None

    def clean(self):
        super().clean()
        # Validate latitude/longitude bounds
        if self.latitude is not None and (self.latitude < -90 or self.latitude > 90):
            raise ValidationError({'latitude': 'Latitude must be between -90 and 90 degrees.'})
        if self.longitude is not None and (self.longitude < -180 or self.longitude > 180):
            raise ValidationError({'longitude': 'Longitude must be between -180 and 180 degrees.'})

        # Validate role consistency
        if self.user_id:
            validate_organization_type_for_role(self.user.role, self.org_type)

    def __str__(self):
        return f"{self.name} ({self.get_org_type_display()}) - [{self.verification_status}]"


class OrganizationDocument(models.Model):
    """
    Uploaded verification evidence (FSSAI, 80G, NGO Darpan, etc.).
    Stored privately outside public media storage.
    """
    class ReviewStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending Review'
        APPROVED = 'APPROVED', 'Document Approved'
        REJECTED = 'REJECTED', 'Document Rejected'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        OrganizationProfile,
        on_delete=models.CASCADE,
        related_name='documents'
    )
    document_type = models.CharField(max_length=50, choices=DocumentType.choices)
    file = models.FileField(
        storage=get_private_document_storage,
        upload_to=organization_document_upload_path,
        help_text="Securely stored private document file outside public media root"
    )
    original_filename = models.CharField(max_length=255)
    file_size_bytes = models.PositiveIntegerField()
    content_type = models.CharField(max_length=100)

    # Document-level Review & Notes
    review_status = models.CharField(
        max_length=20,
        choices=ReviewStatus.choices,
        default=ReviewStatus.PENDING
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_documents'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True, default='')

    uploaded_at = models.DateTimeField(auto_now_add=True)

    @property
    def is_approved(self):
        return self.review_status == self.ReviewStatus.APPROVED

    @property
    def is_rejected(self):
        return self.review_status == self.ReviewStatus.REJECTED

    def __str__(self):
        return f"{self.get_document_type_display()} for {self.organization.name} [{self.review_status}]"


class ImmutableQuerySet(models.QuerySet):
    """QuerySet that blocks bulk update and delete operations on audit logs."""
    def update(self, *args, **kwargs):
        raise PermissionDenied("Bulk update is disallowed on immutable audit logs.")

    def delete(self, *args, **kwargs):
        raise PermissionDenied("Bulk delete is disallowed on immutable audit logs.")


class ImmutableManager(models.Manager.from_queryset(ImmutableQuerySet)):
    """Manager ensuring all queries return ImmutableQuerySet."""
    pass


class OrganizationVerificationEvent(models.Model):
    """
    Immutable audit log recording every verification lifecycle event.
    Protected at database-level via on_delete=PROTECT and application-level via overridden methods.
    """
    class EventType(models.TextChoices):
        SUBMITTED = 'SUBMITTED', 'Submitted for Verification'
        APPROVED = 'APPROVED', 'Approved by Administrator'
        REJECTED = 'REJECTED', 'Rejected by Administrator'
        RESUBMITTED = 'RESUBMITTED', 'Resubmitted by Organization Owner'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        OrganizationProfile,
        on_delete=models.PROTECT,  # Prevents deletion of OrganizationProfile while audit records exist
        related_name='verification_events'
    )
    event_type = models.CharField(max_length=20, choices=EventType.choices)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='recorded_verification_events',
        help_text="User who initiated this event (Admin reviewer or Organization owner)"
    )
    previous_status = models.CharField(max_length=20)
    new_status = models.CharField(max_length=20)
    notes = models.TextField(blank=True, default='', help_text="Mandatory rejection notes or review commentary")
    created_at = models.DateTimeField(auto_now_add=True)

    objects = ImmutableManager()

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        # Enforce instance-level immutability
        if self.pk and not self._state.adding:
            raise PermissionDenied("OrganizationVerificationEvent records are immutable and cannot be updated.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Enforce instance-level append-only audit trail
        raise PermissionDenied("OrganizationVerificationEvent records are immutable and cannot be deleted.")

    def __str__(self):
        return f"{self.organization.name} - {self.event_type} ({self.created_at:%Y-%m-%d %H:%M})"
