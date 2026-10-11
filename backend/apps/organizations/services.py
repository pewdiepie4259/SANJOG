from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError, PermissionDenied
from django.utils.text import get_valid_filename

from .models import (
    OrganizationProfile, 
    OrganizationDocument, 
    OrganizationVerificationEvent,
    private_document_storage
)
from .validators import (
    OrganizationType, 
    DocumentType, 
    REQUIRED_DOCUMENTS_BY_ORG_TYPE,
    validate_organization_type_for_role,
    validate_file_security
)
from .exceptions import ConcurrencyConflictError


class OrganizationService:
    """
    Service layer handling organization profile registration, updates, and submission.
    Decoupled from views and serializers.
    """

    @classmethod
    @transaction.atomic
    def create_profile(cls, user, name, org_type, contact_person, contact_email, contact_phone,
                       address_line1, city, state, postal_code, country='India',
                       address_line2='', registration_number=None, latitude=None, longitude=None):
        """
        Creates an organization profile for an authenticated DONOR or RECEIVER user.
        Enforces one-to-one organization profile constraint per user account.
        """
        if not user or not user.is_authenticated:
            raise PermissionDenied("User must be authenticated to create an organization profile.")

        if user.role == 'VOLUNTEER':
            raise PermissionDenied("Volunteers operate as individual agents and cannot register organization profiles.")

        if hasattr(user, 'organization_profile'):
            raise ValidationError({'user': 'This user account is already associated with an organization profile.'})

        # Validate role consistency with organization type
        validate_organization_type_for_role(user.role, org_type)

        # Validate latitude/longitude bounds
        if latitude is not None and (latitude < -90 or latitude > 90):
            raise ValidationError({'latitude': 'Latitude must be between -90 and 90 degrees.'})
        if longitude is not None and (longitude < -180 or longitude > 180):
            raise ValidationError({'longitude': 'Longitude must be between -180 and 180 degrees.'})

        # Validate registration number uniqueness if provided
        cleaned_reg = registration_number.strip() if registration_number and registration_number.strip() else None
        if cleaned_reg:
            if OrganizationProfile.objects.filter(registration_number__iexact=cleaned_reg).exists():
                raise ValidationError({'registration_number': 'An organization with this registration number already exists.'})

        org = OrganizationProfile.objects.create(
            user=user,
            name=name.strip(),
            org_type=org_type,
            registration_number=cleaned_reg,
            contact_person=contact_person.strip(),
            contact_email=contact_email.strip().lower(),
            contact_phone=contact_phone.strip(),
            address_line1=address_line1.strip(),
            address_line2=address_line2.strip() if address_line2 else '',
            city=city.strip(),
            state=state.strip(),
            postal_code=postal_code.strip(),
            country=country.strip() if country else 'India',
            latitude=latitude,
            longitude=longitude,
            verification_status=OrganizationProfile.VerificationStatus.DRAFT
        )
        return org

    @classmethod
    @transaction.atomic
    def update_profile(cls, user, org_id, **kwargs):
        """
        Updates organization profile fields while in DRAFT or REJECTED status.
        Locked from editing when status is PENDING or APPROVED.
        """
        org = OrganizationProfile.objects.select_for_update().get(id=org_id)

        if org.user != user and not user.is_admin_user:
            raise PermissionDenied("You do not have permission to modify this organization profile.")

        if org.verification_status == OrganizationProfile.VerificationStatus.PENDING:
            raise ValidationError("Organization profile is currently locked under administrative review.")

        # If org_type is being updated, validate role consistency
        if 'org_type' in kwargs:
            validate_organization_type_for_role(org.user.role, kwargs['org_type'])
            org.org_type = kwargs['org_type']

        # Validate coordinate updates
        if 'latitude' in kwargs:
            lat = kwargs['latitude']
            if lat is not None and (lat < -90 or lat > 90):
                raise ValidationError({'latitude': 'Latitude must be between -90 and 90 degrees.'})
            org.latitude = lat

        if 'longitude' in kwargs:
            lon = kwargs['longitude']
            if lon is not None and (lon < -180 or lon > 180):
                raise ValidationError({'longitude': 'Longitude must be between -180 and 180 degrees.'})
            org.longitude = lon

        # Registration number update uniqueness
        if 'registration_number' in kwargs:
            reg_num = kwargs['registration_number']
            cleaned_reg = reg_num.strip() if reg_num and reg_num.strip() else None
            if cleaned_reg and cleaned_reg != org.registration_number:
                if OrganizationProfile.objects.filter(registration_number__iexact=cleaned_reg).exclude(id=org.id).exists():
                    raise ValidationError({'registration_number': 'An organization with this registration number already exists.'})
            org.registration_number = cleaned_reg

        # Updatable fields
        for field in ['name', 'contact_person', 'contact_email', 'contact_phone',
                      'address_line1', 'address_line2', 'city', 'state', 'postal_code', 'country']:
            if field in kwargs:
                val = kwargs[field]
                setattr(org, field, val.strip() if isinstance(val, str) else val)

        org.save()
        return org

    @classmethod
    @transaction.atomic
    def submit_for_verification(cls, user, org_id):
        """
        Submits an organization for administrative verification (DRAFT/REJECTED -> PENDING).
        Enforces Gate 1: All mandatory documents for the org type must exist and have non-rejected status.
        """
        org = OrganizationProfile.objects.select_for_update().get(id=org_id)

        if org.user != user and not user.is_admin_user:
            raise PermissionDenied("You do not have permission to submit this organization.")

        if org.verification_status == OrganizationProfile.VerificationStatus.PENDING:
            raise ValidationError("Organization is already submitted and pending review.")

        if org.verification_status == OrganizationProfile.VerificationStatus.APPROVED:
            raise ValidationError("Organization is already approved.")

        # Gate 1: Check mandatory document requirements
        required_types = REQUIRED_DOCUMENTS_BY_ORG_TYPE.get(org.org_type, [])
        missing_docs = []
        rejected_without_replacement = []

        for req_type in required_types:
            docs = org.documents.filter(document_type=req_type)
            if not docs.exists():
                missing_docs.append(req_type.label if hasattr(req_type, 'label') else str(req_type))
            else:
                # Must have at least one document that is NOT rejected (i.e. PENDING or APPROVED)
                has_active = docs.filter(
                    review_status__in=[OrganizationDocument.ReviewStatus.PENDING, OrganizationDocument.ReviewStatus.APPROVED]
                ).exists()
                if not has_active:
                    rejected_without_replacement.append(req_type.label if hasattr(req_type, 'label') else str(req_type))

        if missing_docs:
            raise ValidationError({
                'documents': f"Cannot submit for verification: Missing mandatory document(s): {', '.join(missing_docs)} for organization type '{org.get_org_type_display()}'."
            })

        if rejected_without_replacement:
            raise ValidationError({
                'documents': f"Cannot submit for verification: Mandatory document(s): {', '.join(rejected_without_replacement)} have been rejected and require an active replacement file."
            })

        prev_status = org.verification_status
        is_resubmission = (prev_status == OrganizationProfile.VerificationStatus.REJECTED)
        org.verification_status = OrganizationProfile.VerificationStatus.PENDING
        org.save()

        # Record immutable audit event
        event_type = (
            OrganizationVerificationEvent.EventType.RESUBMITTED 
            if is_resubmission 
            else OrganizationVerificationEvent.EventType.SUBMITTED
        )
        OrganizationVerificationEvent.objects.create(
            organization=org,
            event_type=event_type,
            actor=user,
            previous_status=prev_status,
            new_status=org.verification_status,
            notes='Organization profile submitted for administrative verification.'
        )
        return org


class DocumentService:
    """
    Service layer handling verification document upload, deletion, and individual review.
    Enforces fail-safe storage cleanup and transactional consistency.
    """

    @classmethod
    def upload_document(cls, user, org_id, document_type, uploaded_file):
        """
        Uploads and creates an OrganizationDocument with fail-safe disk cleanup.
        Never references uninitialized variables.
        """
        if not uploaded_file:
            raise ValidationError({'file': 'No file was provided.'})

        # Deep security & magic header verification
        detected_mime = validate_file_security(uploaded_file)

        org = OrganizationProfile.objects.get(id=org_id)
        if org.user != user and not user.is_admin_user:
            raise PermissionDenied("You do not have permission to upload documents for this organization.")

        if org.verification_status == OrganizationProfile.VerificationStatus.PENDING:
            raise ValidationError("Cannot upload documents while organization is pending administrative review.")

        sanitized_filename = get_valid_filename(uploaded_file.name)
        saved_file_name = None

        try:
            with transaction.atomic():
                doc = OrganizationDocument(
                    organization=org,
                    document_type=document_type,
                    original_filename=sanitized_filename,
                    file_size_bytes=uploaded_file.size,
                    content_type=detected_mime,
                    file=uploaded_file,
                    review_status=OrganizationDocument.ReviewStatus.PENDING
                )
                doc.save()
                saved_file_name = doc.file.name
                return doc
        except Exception:
            # If DB save failed after storage backend wrote the file to disk, clean it up immediately
            if saved_file_name and private_document_storage.exists(saved_file_name):
                private_document_storage.delete(saved_file_name)
            raise

    @classmethod
    @transaction.atomic
    def delete_document(cls, user, document_id):
        """
        Deletes a document from database and private storage.
        Executes physical file removal only after the database transaction successfully commits.
        """
        doc = OrganizationDocument.objects.select_for_update().get(id=document_id)

        if doc.organization.user != user and not user.is_admin_user:
            raise PermissionDenied("You do not have permission to delete this document.")

        if doc.organization.verification_status == OrganizationProfile.VerificationStatus.PENDING:
            raise ValidationError("Cannot delete documents while organization is pending verification.")

        file_name_to_delete = doc.file.name
        doc.delete()

        # Delete physical file on disk only after DB transaction commits
        transaction.on_commit(lambda: private_document_storage.delete(file_name_to_delete))

    @classmethod
    @transaction.atomic
    def review_document(cls, admin_user, document_id, decision, rejection_reason=''):
        """
        Admin review action for an individual document.
        Does not affect other documents.
        """
        if not admin_user.is_admin_user:
            raise PermissionDenied("Only administrators can review documents.")

        doc = OrganizationDocument.objects.select_for_update().get(id=document_id)

        if decision == OrganizationDocument.ReviewStatus.REJECTED:
            if not rejection_reason or not rejection_reason.strip():
                raise ValidationError({'rejection_reason': 'A rejection reason is mandatory when rejecting a document.'})
            doc.review_status = OrganizationDocument.ReviewStatus.REJECTED
            doc.rejection_reason = rejection_reason.strip()
        elif decision == OrganizationDocument.ReviewStatus.APPROVED:
            doc.review_status = OrganizationDocument.ReviewStatus.APPROVED
            doc.rejection_reason = ''
        else:
            raise ValidationError({'decision': 'Invalid review decision. Must be APPROVED or REJECTED.'})

        doc.reviewed_by = admin_user
        doc.reviewed_at = timezone.now()
        doc.save()
        return doc


class VerificationService:
    """
    Administrative verification service governing approval, rejection, and concurrency.
    """

    @classmethod
    @transaction.atomic
    def approve_organization(cls, admin_user, org_id):
        """
        Approves an organization following strict Gate 2 document eligibility verification.
        Requires that every mandatory document type has an approved document.
        Optional documents are not automatically approved.
        """
        if not admin_user.is_admin_user:
            raise PermissionDenied("Only authorized administrators can approve organizations.")

        # Row-level lock in PostgreSQL
        org = OrganizationProfile.objects.select_for_update().get(id=org_id)

        # Pre-condition check against concurrent conflict
        if org.verification_status != OrganizationProfile.VerificationStatus.PENDING:
            raise ConcurrencyConflictError(
                f"Organization is no longer pending verification (Current status: {org.verification_status}). "
                "Another administrator may have already processed this review."
            )

        # Gate 2: Enforce mandatory document approval policy
        required_types = REQUIRED_DOCUMENTS_BY_ORG_TYPE.get(org.org_type, [])
        unapproved_mandatory = []

        for req_type in required_types:
            has_approved = org.documents.filter(
                document_type=req_type,
                review_status=OrganizationDocument.ReviewStatus.APPROVED
            ).exists()
            if not has_approved:
                unapproved_mandatory.append(req_type.label if hasattr(req_type, 'label') else str(req_type))

        if unapproved_mandatory:
            raise ValidationError({
                'documents': f"Cannot approve organization: Mandatory document(s) have not been individually approved: {', '.join(unapproved_mandatory)}."
            })

        now = timezone.now()
        prev_status = org.verification_status
        org.verification_status = OrganizationProfile.VerificationStatus.APPROVED
        org.verified_by = admin_user
        org.verified_at = now
        org.rejection_reason = ''
        org.save()

        # Immutable audit trail
        OrganizationVerificationEvent.objects.create(
            organization=org,
            event_type=OrganizationVerificationEvent.EventType.APPROVED,
            actor=admin_user,
            previous_status=prev_status,
            new_status=org.verification_status,
            notes='Organization successfully verified and approved.'
        )
        return org

    @classmethod
    @transaction.atomic
    def reject_organization(cls, admin_user, org_id, rejection_reason):
        """
        Atomically rejects an organization with mandatory rejection notes.
        """
        if not admin_user.is_admin_user:
            raise PermissionDenied("Only authorized administrators can reject organizations.")

        if not rejection_reason or not rejection_reason.strip():
            raise ValidationError({'rejection_reason': 'A specific rejection reason must be provided.'})

        org = OrganizationProfile.objects.select_for_update().get(id=org_id)

        if org.verification_status != OrganizationProfile.VerificationStatus.PENDING:
            raise ConcurrencyConflictError(
                f"Organization is no longer pending verification (Current status: {org.verification_status}). "
                "Another administrator may have already processed this review."
            )

        now = timezone.now()
        prev_status = org.verification_status
        org.verification_status = OrganizationProfile.VerificationStatus.REJECTED
        org.verified_by = admin_user
        org.verified_at = now
        org.rejection_reason = rejection_reason.strip()
        org.save()

        # Immutable audit trail
        OrganizationVerificationEvent.objects.create(
            organization=org,
            event_type=OrganizationVerificationEvent.EventType.REJECTED,
            actor=admin_user,
            previous_status=prev_status,
            new_status=org.verification_status,
            notes=rejection_reason.strip()
        )
        return org
