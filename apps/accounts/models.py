import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    """
    Custom user model for SANJOG Food Rescue OS.
    Extends Django's AbstractUser to support role-based authorization.
    """
    class RoleChoices(models.TextChoices):
        DONOR = 'DONOR', 'Food Donor'
        RECEIVER = 'RECEIVER', 'Food Receiver (NGO/Shelter)'
        VOLUNTEER = 'VOLUNTEER', 'Rescue Volunteer'
        ADMIN = 'ADMIN', 'Platform Administrator'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(
        max_length=20,
        choices=RoleChoices.choices,
        default=RoleChoices.DONOR,
        help_text="Primary operational role within SANJOG platform"
    )
    phone_number = models.CharField(max_length=20, blank=True, null=True, unique=True)
    is_email_verified = models.BooleanField(default=False)

    @property
    def is_donor(self):
        return self.role == self.RoleChoices.DONOR

    @property
    def is_receiver(self):
        return self.role == self.RoleChoices.RECEIVER

    @property
    def is_volunteer(self):
        return self.role == self.RoleChoices.VOLUNTEER

    @property
    def is_admin_user(self):
        return self.role == self.RoleChoices.ADMIN or self.is_staff or self.is_superuser

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
