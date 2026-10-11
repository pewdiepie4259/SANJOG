from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import OrganizationProfile, OrganizationDocument, OrganizationVerificationEvent
from .validators import OrganizationType, DocumentType, validate_organization_type_for_role


class OrganizationDocumentSerializer(serializers.ModelSerializer):
    """DRF Serializer for OrganizationDocument metadata."""
    document_type_display = serializers.CharField(source='get_document_type_display', read_only=True)
    review_status_display = serializers.CharField(source='get_review_status_display', read_only=True)
    reviewed_by_username = serializers.CharField(source='reviewed_by.username', read_only=True)

    class Meta:
        model = OrganizationDocument
        fields = (
            'id', 'document_type', 'document_type_display', 'original_filename',
            'file_size_bytes', 'content_type', 'review_status', 'review_status_display',
            'reviewed_by', 'reviewed_by_username', 'reviewed_at', 'rejection_reason',
            'uploaded_at'
        )
        read_only_fields = (
            'id', 'original_filename', 'file_size_bytes', 'content_type',
            'review_status', 'reviewed_by', 'reviewed_at', 'rejection_reason', 'uploaded_at'
        )


class OrganizationVerificationEventSerializer(serializers.ModelSerializer):
    """DRF Serializer for immutable audit verification timeline events."""
    event_type_display = serializers.CharField(source='get_event_type_display', read_only=True)
    actor_username = serializers.CharField(source='actor.username', read_only=True)

    class Meta:
        model = OrganizationVerificationEvent
        fields = (
            'id', 'event_type', 'event_type_display', 'actor', 'actor_username',
            'previous_status', 'new_status', 'notes', 'created_at'
        )
        read_only_fields = fields


class OrganizationProfileSerializer(serializers.ModelSerializer):
    """DRF Serializer for OrganizationProfile details with nested documents and audit timeline."""
    org_type_display = serializers.CharField(source='get_org_type_display', read_only=True)
    verification_status_display = serializers.CharField(source='get_verification_status_display', read_only=True)
    user_role = serializers.CharField(source='user.role', read_only=True)
    documents = OrganizationDocumentSerializer(many=True, read_only=True)
    verification_events = OrganizationVerificationEventSerializer(many=True, read_only=True)

    class Meta:
        model = OrganizationProfile
        fields = (
            'id', 'user', 'user_role', 'name', 'org_type', 'org_type_display',
            'registration_number', 'contact_person', 'contact_email', 'contact_phone',
            'address_line1', 'address_line2', 'city', 'state', 'postal_code', 'country',
            'latitude', 'longitude', 'verification_status', 'verification_status_display',
            'rejection_reason', 'verified_by', 'verified_at', 'created_at', 'updated_at',
            'documents', 'verification_events'
        )
        read_only_fields = (
            'id', 'user', 'user_role', 'verification_status', 'rejection_reason',
            'verified_by', 'verified_at', 'created_at', 'updated_at'
        )

    def validate_latitude(self, value):
        if value is not None and (value < -90 or value > 90):
            raise serializers.ValidationError("Latitude must be between -90 and 90 degrees.")
        return value

    def validate_longitude(self, value):
        if value is not None and (value < -180 or value > 180):
            raise serializers.ValidationError("Longitude must be between -180 and 180 degrees.")
        return value


class OrganizationCreateSerializer(serializers.ModelSerializer):
    """DRF Serializer for creating an organization profile."""

    class Meta:
        model = OrganizationProfile
        fields = (
            'name', 'org_type', 'registration_number', 'contact_person',
            'contact_email', 'contact_phone', 'address_line1', 'address_line2',
            'city', 'state', 'postal_code', 'country', 'latitude', 'longitude'
        )

    def validate(self, attrs):
        user = self.context['request'].user
        if hasattr(user, 'organization_profile'):
            raise serializers.ValidationError({'non_field_errors': 'This user account is already associated with an organization profile.'})
        try:
            validate_organization_type_for_role(user.role, attrs['org_type'])
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message_dict if hasattr(e, 'message_dict') else str(e))
        return attrs


class AdminDocumentReviewSerializer(serializers.Serializer):
    """DRF Serializer for reviewing individual documents."""
    decision = serializers.ChoiceField(choices=['APPROVED', 'REJECTED'])
    rejection_reason = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        if attrs['decision'] == 'REJECTED' and not attrs.get('rejection_reason', '').strip():
            raise serializers.ValidationError({'rejection_reason': 'Rejection reason is required when rejecting a document.'})
        return attrs


class AdminOrganizationRejectSerializer(serializers.Serializer):
    """DRF Serializer for rejecting an organization."""
    rejection_reason = serializers.CharField(required=True)

    def validate_rejection_reason(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Rejection reason cannot be blank.")
        return value.strip()
