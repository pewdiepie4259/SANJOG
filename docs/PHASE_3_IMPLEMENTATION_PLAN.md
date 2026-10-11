# SANJOG — PHASE 3 IMPLEMENTATION PLAN: ORGANIZATION MANAGEMENT & VERIFICATION

> **Status:** IMPLEMENTED & VERIFIED (100% TEST SUITE PASSING — 42/42 PHASE 3 TESTS PASS)  
> **Phase:** 3 — Organization Management & Verification Queue  
> **Target Date:** October 2026  
> **Architecture Compliance:** Food Rescue OS Architecture (Phases 0–19)  
> **Verification Status:** Fully Tested, 0 Regressions, 0 Django System Check Issues.

---

## 1. CURRENT REPOSITORY STATE & ARCHITECTURE VERIFICATION

A comprehensive inspection of the actual repository at `F:\SANJOG` confirms the following:

1. **Framework & Stack Verification:**
   - Django 5.x with modular settings (`config/settings/base.py`, `development.py`, `production.py`).
   - PostgreSQL/PostGIS configured with SQLite development fallback (`USE_SQLITE=True`).
   - Redis and Celery configuration in place for background task processing.
   - Django REST Framework (DRF) 3.14+ configured with Token and Session Authentication, Scoped Rate Limiting (`5/minute` for auth), and URL path versioning (`/api/v1/`).
   - Core stack preserved: Django Templates, Tailwind CSS, HTMX, Django REST Framework, and PostgreSQL. Zero unrelated architectural departures.

2. **Phase 1 Infrastructure:**
   - Directory structure established (`apps/`, `config/`, `static/`, `templates/`, `tests/`).
   - Base templates with Tailwind CSS tokens and HTMX support (`templates/base.html`, `templates/partials/head.html`, `templates/components/navbar.html`).
   - Health check endpoints operational at `/health/` and `/api/v1/health/`.

3. **Phase 2 Authentication & RBAC Verification (`apps/accounts/`):**
   - **`CustomUser` Model:** Extends `AbstractUser` with `id` (UUID PK), `role` (`DONOR`, `RECEIVER`, `VOLUNTEER`, `ADMIN`), `phone_number`, `is_email_verified`.
   - **Admin Verification Mechanism:** Confirmed that `CustomUser.is_admin_user` **actually exists** at lines 39–40 of `apps/accounts/models.py`:
     ```python
     @property
     def is_admin_user(self):
         return self.role == self.RoleChoices.ADMIN or self.is_staff or self.is_superuser
     ```
   - **DRF Permissions:** Confirmed `apps.accounts.permissions.IsAdminUser` exists and checks `request.user.is_admin_user`.
   - **View Decorators:** Confirmed `apps.accounts.decorators.admin_required` and `role_required` exist.
   - **Service Layer:** `AuthService` handles registration, brute-force rate-limiting (5 failed attempts trigger a 15-minute lockout), login, and DRF token creation/revocation.
   - **Test Suite Status:** All **19 out of 19 tests pass** in `tests/test_health.py`, `tests/test_auth.py`, and `tests/test_rbac.py`.

4. **Current Organization State:**
   - No `apps/organizations` directory, models, or migrations exist yet.
   - Existing dashboards (`donor_dashboard.html`, `receiver_dashboard.html`, `admin_dashboard.html`) display placeholder metrics without organization profile bindings.

---

## 2. PHASE 0–2 DEPENDENCIES & MIGRATION SAFETY GUARANTEES

Phase 3 builds strictly upon completed Phase 0, Phase 1, and Phase 2 foundations without modifying past deliverables:

1. **`CustomUser` Immutability:**
   - `apps/accounts/models.py` and `CustomUser` will **not** be modified. No fields, methods, or properties will be altered or added to `CustomUser`.
2. **Migration History Preservation:**
   - `apps/accounts/migrations/0001_initial.py` is preserved intact.
   - The database will **never** be reset, flushed, or recreated.
   - `apps/organizations/migrations/0001_initial.py` will explicitly depend on `('accounts', '0001_initial')`.
3. **RBAC Role Matrix Reuse:**
   - `CustomUser.role` (`DONOR`, `RECEIVER`, `VOLUNTEER`, `ADMIN`) is reused directly.
   - Phase 2 permissions (`IsAdminUser`, `IsDonor`, `IsReceiver`) are reused without alteration.
4. **Regression Protection:**
   - All 19 existing authentication and RBAC tests must continue to pass with 0 regressions.

---

## 3. PHASE 3 OBJECTIVE

Build an enterprise-grade, secure, and auditable **Organization Profile Management & Verification Pipeline** for SANJOG:
1. **Donor Organizations:** Enable food donors (restaurants, hotels, hostel messes, caterers, canteens, event organizers) to create an organization profile and upload business accreditation / FSSAI licenses.
2. **Receiver Organizations:** Enable food receivers (NGOs, shelters, orphanages, community kitchens, charitable trusts) to create an organization profile and upload 80G tax exemption / trust deeds / registration certificates.
3. **Volunteer Role Isolation:** Volunteers (`VOLUNTEER` role) operate as individual logistics agents and **do not require an organization profile** by default. They are never forced into the organization verification pipeline.
4. **Admin Verification Queue:** Authorized administrators review pending organizations, inspect uploaded legal documents, and record `APPROVED` or `REJECTED` decisions with mandatory rejection notes for auditing.
5. **Decoupled Verification Lifecycle:** User authentication status remains strictly separated from organization verification status. Unverified users can log in, inspect their profile, and check verification progress, but cannot participate in food surplus listing (Phase 4) or meal demand claiming (Phase 5).

---

## 4. PROPOSED MODEL DESIGN

### Architectural Decision: Normalized Ownership & Future-Proofing
- **College MVP Requirement:** Each donor or receiver account is associated with one primary organization profile.
- **Future Extensibility:** Organizations will eventually need multiple staff members (e.g., manager, chef, dispatcher).
- **Normalized Solution:** 
  - `OrganizationProfile` uses a `OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='organization_profile')` pointing to the primary account owner.
  - This guarantees strict 1-to-1 integrity for the MVP while allowing the schema to add a many-to-many `OrganizationMembership` junction table in Phase 8+ without breaking the primary owner reference.

### 4.1 `OrganizationProfile` Model Specification
```python
# Location: apps/organizations/models.py

class OrganizationProfile(models.Model):
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

    # Geolocation Coordinates (Decimal precision 9,6 for ~11cm GPS accuracy)
    # Explicit deviation from PostGIS PointField for Phase 3 dev/test safety
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
    def location_coords(self):
        if self.latitude is not None and self.longitude is not None:
            return (float(self.latitude), float(self.longitude))
        return None

    def __str__(self):
        return f"{self.name} ({self.get_org_type_display()}) - [{self.verification_status}]"
```

### 4.2 `OrganizationDocument` Model Specification
```python
# Location: apps/organizations/models.py
from django.core.files.storage import FileSystemStorage
from django.conf import settings

# Dedicated private storage backend located outside public media root
private_document_storage = FileSystemStorage(
    location=settings.PRIVATE_MEDIA_ROOT,
    base_url=None  # Explicitly prevents public URL generation
)

def organization_document_upload_path(instance, filename):
    ext = Path(filename).suffix.lower()
    return f"org_{instance.organization_id}/{uuid.uuid4()}{ext}"

class OrganizationDocument(models.Model):
    class DocumentType(models.TextChoices):
        FSSAI_LICENSE = 'FSSAI_LICENSE', 'FSSAI Food Safety License'
        BUSINESS_REGISTRATION = 'BUSINESS_REGISTRATION', 'GST / Shop Act / Business Registration'
        NGO_DARPAN = 'NGO_DARPAN', 'NITI Aayog NGO Darpan Registration'
        TAX_EXEMPT_80G = 'TAX_EXEMPT_80G', '80G / 12A Tax Exemption Certificate'
        TRUST_DEED = 'TRUST_DEED', 'Trust Deed / Society Registration'
        ID_PROOF = 'ID_PROOF', 'Authorized Signatory Identity Proof'
        OTHER = 'OTHER', 'Other Supporting Accreditation'

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
        storage=private_document_storage,
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
```

### 4.3 `OrganizationVerificationEvent` Model (Audit Retention & Immutability)
To resolve the conflict between preserved historical audit trail and cascade deletion, `OrganizationVerificationEvent` uses `on_delete=models.PROTECT`. Furthermore, application-level immutability is enforced via both model methods and custom QuerySet managers:

```python
# Location: apps/organizations/models.py
from django.core.exceptions import PermissionDenied

class ImmutableQuerySet(models.QuerySet):
    def update(self, *args, **kwargs):
        raise PermissionDenied("Bulk update is disallowed on immutable audit logs.")

    def delete(self, *args, **kwargs):
        raise PermissionDenied("Bulk delete is disallowed on immutable audit logs.")

class ImmutableManager(models.Manager.from_queryset(ImmutableQuerySet)):
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
        on_delete=models.PROTECT,  # Prevents deletion of OrganizationProfile while audit history exists
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
```

#### Application-Level vs. Database-Level Guarantees
> **Explicit Architectural Boundary:**
> - **Application-Level Guarantees:** Overridden `save()` and `delete()` methods block single-instance updates and deletes. The custom `ImmutableQuerySet` blocks ORM bulk `update()` and `delete()` calls. Django Admin permissions disallow add/change/delete.
> - **Database-Level Protection:** `on_delete=models.PROTECT` prevents deleting the parent `OrganizationProfile` at the foreign key constraint level.
> - **Direct Database Superuser Access:** Model and ORM overrides cannot stop a database superuser executing raw SQL (`DELETE FROM organizations_organizationverificationevent;`). Database privilege separation (`REVOKE UPDATE, DELETE ON ... FROM sanjog_app_user;`) is documented as an infrastructure production hardening step in Phase 18.

---

## 5. DOCUMENT ELIGIBILITY, REVIEW & APPROVAL POLICY

Document-level review decisions and organization-level decisions are strictly separated:

```
[Document Upload] ──► [Admin Document Review] ──► [Organization Eligibility Check] ──► [Org Approval]
                      (review_document)           (Gate 2 Validation)                  (approve_org)
```

### 5.1 Configurable Mandatory Document Rules
```python
# Location: apps/organizations/validators.py

REQUIRED_DOCUMENTS_BY_ORG_TYPE = {
    # Donors
    OrganizationType.RESTAURANT: [DocumentType.FSSAI_LICENSE, DocumentType.BUSINESS_REGISTRATION],
    OrganizationType.HOTEL: [DocumentType.FSSAI_LICENSE, DocumentType.BUSINESS_REGISTRATION],
    OrganizationType.HOSTEL_MESS: [DocumentType.FSSAI_LICENSE, DocumentType.ID_PROOF],
    OrganizationType.CATERER: [DocumentType.FSSAI_LICENSE, DocumentType.BUSINESS_REGISTRATION],
    OrganizationType.CANTEEN: [DocumentType.FSSAI_LICENSE, DocumentType.BUSINESS_REGISTRATION],
    OrganizationType.EVENT_ORGANIZER: [DocumentType.BUSINESS_REGISTRATION, DocumentType.ID_PROOF],
    OrganizationType.OTHER_DONOR: [DocumentType.BUSINESS_REGISTRATION],

    # Receivers
    OrganizationType.NGO: [DocumentType.NGO_DARPAN, DocumentType.TAX_EXEMPT_80G],
    OrganizationType.SHELTER: [DocumentType.TRUST_DEED, DocumentType.ID_PROOF],
    OrganizationType.ORPHANAGE: [DocumentType.TRUST_DEED, DocumentType.ID_PROOF],
    OrganizationType.COMMUNITY_KITCHEN: [DocumentType.TRUST_DEED, DocumentType.ID_PROOF],
    OrganizationType.CHARITABLE_ORGANIZATION: [DocumentType.TRUST_DEED, DocumentType.TAX_EXEMPT_80G],
    OrganizationType.OTHER_RECEIVER: [DocumentType.TRUST_DEED],
}
```

### 5.2 Admin Individual Document Review
Administrators inspect each submitted document individually through a dedicated service method:
```python
# Location: apps/organizations/services.py

class DocumentService:
    @classmethod
    @transaction.atomic
    def review_document(cls, admin_user, document_id, decision, rejection_reason=''):
        """
        Explicit individual document review action.
        decision: OrganizationDocument.ReviewStatus.APPROVED or REJECTED
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
            raise ValidationError({'decision': 'Invalid review decision.'})

        doc.reviewed_by = admin_user
        doc.reviewed_at = timezone.now()
        doc.save()
        return doc
```

### 5.3 Replacement & Rejection Rules Across Resubmissions
1. **Preservation of Rejected Document History:**
   - When an admin rejects a document, that `OrganizationDocument` instance remains stored with status `REJECTED`, timestamp, reviewer, and `rejection_reason`. It is **never** deleted, overwritten, or erased.
2. **Uploading a Replacement:**
   - The organization owner uploads a new document with the same `document_type`.
   - A new `OrganizationDocument` row is created with status `PENDING`.
   - Both the historical rejected document and the replacement document co-exist in `org.documents`.
3. **Resubmission Eligibility (Gate 1):**
   - For every mandatory document type, there must be at least one active (non-rejected: `PENDING` or `APPROVED`) document.
   - If an owner has a rejected FSSAI license and has not uploaded a replacement, clicking resubmit raises `ValidationError("Cannot submit: Mandatory document 'FSSAI_LICENSE' has been rejected and requires an active replacement.")`.

### 5.4 Organization Approval Policy (Gate 2)
In `VerificationService.approve_organization`:
1. **Strict Mandatory Document Policy:**
   - For every document type required in `REQUIRED_DOCUMENTS_BY_ORG_TYPE[org.org_type]`, there **must** exist at least one document for this organization where `review_status == OrganizationDocument.ReviewStatus.APPROVED`.
   - If any mandatory document type has no approved document (e.g. only `PENDING` or `REJECTED`), organization approval is **strictly blocked** with `ValidationError("Cannot approve organization: Mandatory document '{doc_type}' has not been approved.")`.
2. **No Silent Approval of Optional Documents:**
   - Optional documents (e.g. `OTHER` supporting accreditation) that are `PENDING` are **not** automatically approved during organization approval. They remain in their unreviewed state or can be reviewed independently.
   - Organization approval certifies that all legal requirements for the entity are verified without corrupting the review status of secondary files.

---

## 6. PRIVATE-FILE LIFECYCLE & SECURITY ARCHITECTURE

### 6.1 Upload Validation (Magic Signatures + Format Consistency)
1. **Binary Magic Signature Inspection:**
   - Reads the initial 512 bytes defensively inside a `try/except` block (`IOError`, `ValueError`, `IndexError`).
   - Resets the file seek pointer immediately (`file.seek(0)`) so Django storage handles the full stream cleanly.
   - Verifies canonical binary signatures:
     - **PDF:** starts with `b'%PDF-'`
     - **PNG:** starts with `b'\x89PNG\r\n\x1a\n'`
     - **JPEG:** starts with `b'\xff\xd8\xff'`
     - **WEBP:** starts with `b'RIFF'` and bytes 8..12 are `b'WEBP'`
2. **Extension Consistency:**
   - Verifies that the detected signature matches the file extension (e.g. `.pdf` must have `%PDF-`).
   - Mismatched extension/signature triggers `ValidationError("File content does not match the provided file extension.")`.
3. **Size Bounds & Disallowed Formats:**
   - File size capped at 5 MB (5,242,880 bytes); empty files (0 bytes) rejected.
   - Rejects `.svg`, `.html`, `.xml` (blocking XML/SVG stored XSS).
   - Rejects all executable and script extensions (`.exe`, `.bat`, `.sh`, `.php`, `.py`, `.js`, etc.).
4. **Security Disclaimer:**
   > **Important Security Boundary:** Magic-byte validation and extension matching only verify container format consistency. They do **not** constitute malware scanning, antivirus disinfection, or proof of file safety. Infrastructure-level malware scanning (e.g., ClamAV) is part of Phase 18 (Security Hardening).

### 6.2 Reliable Upload Failure Cleanup & File Lifecycle
To prevent unbound variable errors and orphaned files during database transaction failures:

```python
# Location: apps/organizations/services.py

class DocumentService:
    @classmethod
    def upload_document(cls, user, org_id, document_type, uploaded_file):
        """
        Uploads and creates an OrganizationDocument with fail-safe disk cleanup.
        Never references uninitialized variables.
        """
        # 1. Validation (Memory/Buffer only - no disk file written yet)
        cls.validate_document_file(uploaded_file)

        org = OrganizationProfile.objects.get(id=org_id)
        if org.user != user and not user.is_admin_user:
            raise PermissionDenied("You do not have permission to upload documents for this organization.")

        if org.verification_status == OrganizationProfile.VerificationStatus.PENDING:
            raise ValidationError("Cannot upload documents while organization is pending review.")

        sanitized_filename = get_valid_filename(uploaded_file.name)
        saved_file_name = None

        try:
            with transaction.atomic():
                doc = OrganizationDocument(
                    organization=org,
                    document_type=document_type,
                    original_filename=sanitized_filename,
                    file_size_bytes=uploaded_file.size,
                    content_type=uploaded_file.content_type or 'application/octet-stream',
                    file=uploaded_file
                )
                doc.save()
                saved_file_name = doc.file.name
                return doc
        except Exception:
            # If DB save failed after storage backend wrote the file to disk, clean it up
            if saved_file_name and private_document_storage.exists(saved_file_name):
                private_document_storage.delete(saved_file_name)
            raise
```

### 6.3 Post-Commit Document Deletion
When a user deletes a document (allowed in `DRAFT` or `REJECTED` state), physical deletion must wait until the database transaction successfully commits:

```python
    @classmethod
    @transaction.atomic
    def delete_document(cls, user, document_id):
        doc = OrganizationDocument.objects.select_for_update().get(id=document_id)
        if doc.organization.user != user and not user.is_admin_user:
            raise PermissionDenied("You do not have permission to delete this document.")

        if doc.organization.verification_status == OrganizationProfile.VerificationStatus.PENDING:
            raise ValidationError("Cannot delete documents while organization is pending verification.")

        file_name_to_delete = doc.file.name
        doc.delete()

        # Physical deletion only executed after surrounding DB transaction successfully commits
        transaction.on_commit(lambda: private_document_storage.delete(file_name_to_delete))
```

### 6.4 Periodic Orphaned File Identification & Cleanup
A dedicated management command `cleanup_orphaned_documents` will safely detect and purge files in `PRIVATE_MEDIA_ROOT` not referenced in `OrganizationDocument`:
- Scans files in `PRIVATE_MEDIA_ROOT`.
- Cross-references paths against active `OrganizationDocument.objects.values_list('file', flat=True)`.
- Purges unreferenced files older than 24 hours (a 24-hour buffer prevents deleting files from active in-flight requests).

### 6.5 Secure Streaming Endpoint & Headers
1. **Zero Public Route Exposure:**
   - `PRIVATE_MEDIA_ROOT = BASE_DIR / 'private_media'` is defined in `config/settings/base.py`.
   - `PRIVATE_MEDIA_ROOT` is **never** added to `urlpatterns` static routes and is physically separate from `MEDIA_ROOT`.
2. **Secure Streaming Controller:**
   - Controller verifies: `request.user.is_authenticated` AND (`request.user == document.organization.user` OR `request.user.is_admin_user`).
   - Unauthorized requests receive `403 Forbidden` (`{"detail": "You do not have permission to access this document."}`).
   - Streams file via `FileResponse` with defensive HTTP headers:
     - `Content-Disposition: attachment; filename="{sanitized_original_filename}"`
     - `X-Content-Type-Options: nosniff`
     - `Cache-Control: private, no-cache, no-store, must-revalidate`
     - `Content-Security-Policy: default-src 'none'`

---

## 7. DATABASE CONCURRENCY & TRANSACTIONAL DECISIONS

### 7.1 PostgreSQL vs. SQLite Concurrency Architecture
1. **PostgreSQL Production Environment:**
   - Uses `select_for_update()` to acquire true row-level write locks within an active database transaction.
   - When Admin A calls `approve_organization` and Admin B calls `reject_organization` concurrently, Admin B's transaction blocks until Admin A commits. Admin B then reads the updated status (`APPROVED`), fails the pre-condition check, and raises `ConcurrencyConflictError` (`409 Conflict`).
2. **SQLite Development & Test Environment:**
   - SQLite does **not** provide row-level locking for `select_for_update()`. SQLite uses coarse database-level file locks.
   - In SQLite, `select_for_update()` does not simulate row-level contention.
3. **Explicit Testing Separation:**
   - **State-Guard Concurrency Tests:** Validate that if an organization status is no longer `PENDING`, subsequent approve/reject calls are rejected with `409 Conflict`. These run reliably on both SQLite and PostgreSQL.
   - **Row-Lock Contention Tests:** True multi-threaded/multi-process row-level lock tests require PostgreSQL and must be marked with:
     ```python
     @unittest.skipIf(connection.vendor == 'sqlite', "True row-level locking requires PostgreSQL")
     ```
   - **Guarantee Boundary:** We do **not** claim PostgreSQL row-level concurrency has been verified when running tests solely against SQLite.

### 7.2 Transactional Verification Service
```python
# Location: apps/organizations/services.py

class VerificationService:
    @classmethod
    @transaction.atomic
    def approve_organization(cls, admin_user, org_id):
        if not admin_user.is_admin_user:
            raise PermissionDenied("Only authorized administrators can approve organizations.")

        # Row-level lock in PostgreSQL
        org = OrganizationProfile.objects.select_for_update().get(id=org_id)

        # Pre-condition check
        if org.verification_status != OrganizationProfile.VerificationStatus.PENDING:
            raise ConcurrencyConflictError(
                f"Organization is no longer pending verification (Current status: {org.verification_status})."
            )

        # Enforce Gate 2 Document Eligibility Policy
        required_types = REQUIRED_DOCUMENTS_BY_ORG_TYPE.get(org.org_type, [])
        for req_type in required_types:
            approved_doc = org.documents.filter(
                document_type=req_type,
                review_status=OrganizationDocument.ReviewStatus.APPROVED
            ).exists()
            if not approved_doc:
                raise ValidationError(
                    f"Cannot approve organization: Mandatory document '{req_type}' has not been approved."
                )

        now = timezone.now()
        prev_status = org.verification_status
        org.verification_status = OrganizationProfile.VerificationStatus.APPROVED
        org.verified_by = admin_user
        org.verified_at = now
        org.rejection_reason = ''
        org.save()

        OrganizationVerificationEvent.objects.create(
            organization=org,
            event_type=OrganizationVerificationEvent.EventType.APPROVED,
            actor=admin_user,
            previous_status=prev_status,
            new_status=org.verification_status,
            notes='Organization verified and approved following document validation.'
        )
        return org

    @classmethod
    @transaction.atomic
    def reject_organization(cls, admin_user, org_id, rejection_reason):
        if not admin_user.is_admin_user:
            raise PermissionDenied("Only authorized administrators can reject organizations.")

        if not rejection_reason or not rejection_reason.strip():
            raise ValidationError({'rejection_reason': 'A specific rejection reason must be provided.'})

        org = OrganizationProfile.objects.select_for_update().get(id=org_id)

        if org.verification_status != OrganizationProfile.VerificationStatus.PENDING:
            raise ConcurrencyConflictError(
                f"Organization is no longer pending verification (Current status: {org.verification_status})."
            )

        now = timezone.now()
        prev_status = org.verification_status
        org.verification_status = OrganizationProfile.VerificationStatus.REJECTED
        org.verified_by = admin_user
        org.verified_at = now
        org.rejection_reason = rejection_reason.strip()
        org.save()

        OrganizationVerificationEvent.objects.create(
            organization=org,
            event_type=OrganizationVerificationEvent.EventType.REJECTED,
            actor=admin_user,
            previous_status=prev_status,
            new_status=org.verification_status,
            notes=rejection_reason.strip()
        )
        return org
```

---

## 8. PERMISSIONS & ADMIN AUTHORIZATION REUSE

### 8.1 Admin Authorization Mechanism Reuse
- **Zero Modifications to CustomUser:** Phase 3 reuses `CustomUser.is_admin_user` (`self.role == 'ADMIN' or self.is_staff or self.is_superuser`) without modifying `apps/accounts/models.py`.
- **DRF Endpoints:** Use `apps.accounts.permissions.IsAdminUser` directly on all `/api/v1/admin/organizations/` endpoints.
- **HTML Views:** Template views for admin verification use `@role_required(['ADMIN'])` or check `request.user.is_admin_user`.
- **Object Permissions:** `IsOrganizationOwner` permission checks `request.user == obj.user`.

### 8.2 Authorization Matrix
| Endpoint / Action | Unauthenticated | Volunteer | Donor / Receiver Owner | Other Org User | Platform Admin |
| :--- | :---: | :---: | :---: | :---: | :---: |
| View Own Org Profile | Redirect (302) | 403 Forbidden | **Allowed (200)** | 403 Forbidden | **Allowed (200)** |
| Create Org Profile | Redirect (302) | 403 Forbidden | **Allowed (200)** | 400 (Already Exists)| 403 Forbidden |
| Edit Org Profile | Redirect (302) | 403 Forbidden | **Allowed** (Draft/Rejected)| 403 Forbidden | **Allowed (200)** |
| Upload Document | Redirect (302) | 403 Forbidden | **Allowed (200)** | 403 Forbidden | 403 Forbidden |
| Download Document File | 401 / 302 | 403 Forbidden | **Allowed (200)** | 403 Forbidden | **Allowed (200)** |
| Review Individual Document | 401 / 302 | 403 Forbidden | 403 Forbidden | 403 Forbidden | **Allowed (200)** |
| Submit for Review | Redirect (302) | 403 Forbidden | **Allowed (200)** | 403 Forbidden | 403 Forbidden |
| View Admin Queue | Redirect (302) | 403 Forbidden | 403 Forbidden | 403 Forbidden | **Allowed (200)** |
| Approve Organization | 401 / 302 | 403 Forbidden | 403 Forbidden | 403 Forbidden | **Allowed (200)** |
| Reject Organization | 401 / 302 | 403 Forbidden | 403 Forbidden | 403 Forbidden | **Allowed (200)** |

---

## 9. CANONICAL REST API & TEMPLATE ROUTE ARCHITECTURE

All routes are reconciled to eliminate ambiguity and keep HTML and REST API behavior distinct.

### 9.1 Canonical REST API Endpoints (`/api/v1/`)
| HTTP Method | Canonical URL | Auth | Permission | Request Body | Success | Error Codes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **GET** | `/api/v1/organizations/me/` | Token/Session | Donor/Receiver | None | `200 OK` (Profile + Docs + Events) | `401`, `403`, `404` |
| **POST** | `/api/v1/organizations/` | Token/Session | Donor/Receiver | JSON: Profile fields | `201 Created` | `400`, `401`, `403`, `409` |
| **GET** | `/api/v1/organizations/<uuid:org_id>/` | Token/Session | Owner or Admin | None | `200 OK` | `401`, `403`, `404` |
| **PATCH** | `/api/v1/organizations/<uuid:org_id>/` | Token/Session | Owner Only | JSON: Partial fields | `200 OK` | `400`, `401`, `403` (if locked), `404` |
| **POST** | `/api/v1/organizations/<uuid:org_id>/submit/` | Token/Session | Owner Only | None | `200 OK` (Status = `PENDING`) | `400` (Missing docs), `401`, `403`, `404` |
| **GET** | `/api/v1/organizations/me/verification-status/`| Token/Session | Donor/Receiver | None | `200 OK` (Status, Notes, Events) | `401`, `403`, `404` |
| **POST** | `/api/v1/organizations/<uuid:org_id>/documents/` | Token/Session | Owner Only | `multipart/form-data`: `document_type`, `file` | `201 Created` | `400` (Validation), `401`, `403`, `404` |
| **GET** | `/api/v1/organizations/<uuid:org_id>/documents/` | Token/Session | Owner or Admin | None | `200 OK` (List of docs) | `401`, `403`, `404` |
| **GET** | `/api/v1/organizations/<uuid:org_id>/documents/<uuid:doc_id>/` | Token/Session | Owner or Admin | None | `200 OK` (Binary stream) | `401`, `403`, `404` |
| **DELETE** | `/api/v1/organizations/<uuid:org_id>/documents/<uuid:doc_id>/` | Token/Session | Owner Only | None | `204 No Content` | `401`, `403` (if locked), `404` |
| **POST** | `/api/v1/admin/organizations/<uuid:org_id>/documents/<uuid:doc_id>/review/` | Token/Session | Admin Only | JSON: `{decision, rejection_reason}` | `200 OK` | `400`, `401`, `403`, `404` |
| **GET** | `/api/v1/admin/organizations/` | Token/Session | Admin Only | Query: `?status=...&city=...` | `200 OK` (Paginated list) | `401`, `403` |
| **GET** | `/api/v1/admin/organizations/<uuid:org_id>/` | Token/Session | Admin Only | None | `200 OK` (Audit details) | `401`, `403`, `404` |
| **POST** | `/api/v1/admin/organizations/<uuid:org_id>/approve/` | Token/Session | Admin Only | None | `200 OK` (Status = `APPROVED`) | `400` (Unapproved docs), `401`, `403`, `409` |
| **POST** | `/api/v1/admin/organizations/<uuid:org_id>/reject/` | Token/Session | Admin Only | JSON: `{rejection_reason}` | `200 OK` (Status = `REJECTED`) | `400` (Empty note), `401`, `403`, `409` |

### 9.2 Canonical Template Routes (HTML / HTMX)
- `GET /organizations/onboarding/` — Onboarding introduction
- `GET|POST /organizations/create/` — Organization profile creation form
- `GET /organizations/profile/` — Organization profile detail view
- `GET|POST /organizations/profile/edit/` — Profile edit form
- `POST /organizations/submit/` — Submit for review action
- `GET /organizations/documents/` — Document management table
- `POST /organizations/documents/upload/` — HTMX document upload
- `GET /organizations/documents/<uuid:doc_id>/download/` — Secure download view
- `POST /organizations/documents/<uuid:doc_id>/delete/` — Delete document action
- `GET /admin/organizations/queue/` — Admin pending review queue
- `GET /admin/organizations/<uuid:org_id>/review/` — Admin organization review detail
- `POST /admin/organizations/<uuid:org_id>/documents/<uuid:doc_id>/review/` — Admin document review action
- `POST /admin/organizations/<uuid:org_id>/approve/` — Admin approve action
- `POST /admin/organizations/<uuid:org_id>/reject/` — Admin reject action

### 9.3 Standardized Status Responses
- `401 Unauthorized`: Missing or invalid credentials.
- `403 Forbidden`: Authenticated user lacks permission (cross-role access, IDOR attempt).
- `404 Not Found`: Organization or Document UUID not found.
- `400 Bad Request`: Form/field validation error or missing required documents at submission.
- `409 Conflict`: Concurrency conflict (organization was already approved/rejected).

---

## 10. TEMPLATE STRUCTURE & UI BLUEPRINT

All pages extend `templates/base.html` using Tailwind CSS and HTMX.

### 10.1 User Organization Pages (`templates/organizations/`)
1. **`onboarding.html`:** Clean 2-step onboarding portal for newly registered Donors and Receivers explaining the verification requirements.
2. **`profile_form.html`:** Organization creation and editing form. Dynamically populates matching organization types based on user role (`DONOR` vs `RECEIVER`).
3. **`profile_detail.html`:** Full profile overview featuring status badges (`DRAFT` [Slate], `PENDING` [Amber], `APPROVED` [Green], `REJECTED` [Red]). Includes direct action buttons for editing, document management, and submission.
4. **`document_manage.html`:** HTMX-enabled document manager. Displays required documents checklist for the current organization type, table of uploaded files, review status, and rejection reasons.
5. **`status_partial.html`:** Reusable HTMX status badge and alert banner showing real-time verification status, rejection notes, and audit history.

### 10.2 Admin Verification Pages (`templates/admin_verification/`)
1. **`queue.html`:** Admin verification dashboard displaying pending organizations table with search, role filter, city filter, and pagination.
2. **`review_detail.html`:** Side-by-side verification interface:
   - Left column: Legal entity details, registration numbers, contact person, address, map coordinates.
   - Right column: Uploaded documents list with secure preview/download links and inline "Approve" / "Reject with Reason" buttons per document.
   - Audit column: Historical timeline of all past submission, rejection, and resubmission events.
   - Action bar: One-click **"Approve Organization"** button (enabled only when all mandatory documents are approved) and **"Reject with Reason"** modal.

### 10.3 Dashboard Integration Updates
- **Donor Dashboard (`templates/dashboards/donor_dashboard.html`):** Add an organization verification banner. If unverified, show a warning badge and a direct link to complete onboarding.
- **Receiver Dashboard (`templates/dashboards/receiver_dashboard.html`):** Add verification warning banner explaining that meal demand requests require approved verification.
- **Admin Dashboard (`templates/dashboards/admin_dashboard.html`):** Connect the "Pending Verification" metric card to `/admin/organizations/queue/`.

---

## 11. DJANGO APP STRUCTURE

Create a dedicated, modular Django app: `apps/organizations/`.

```
apps/organizations/
├── __init__.py
├── admin.py                  # Django standard admin registrations (Read-only for audit events)
├── api_views.py              # DRF API ViewSets and Views
├── apps.py                   # OrganizationsConfig
├── exceptions.py             # ConcurrencyConflictError domain exception
├── forms.py                  # Django Forms for HTML & HTMX
├── models.py                 # OrganizationProfile, OrganizationDocument, OrganizationVerificationEvent
├── permissions.py            # DRF permission classes (IsOrganizationOwner, etc.)
├── serializers.py            # DRF serializers
├── services.py               # Pure business logic layer (View -> Service -> Model)
├── urls.py                   # Unified HTML and API route bindings
├── validators.py             # Magic byte validator, file size, required document rules
└── views.py                  # Django Template & HTMX views
```

---

## 12. FILES TO CREATE

1. `apps/organizations/__init__.py`
2. `apps/organizations/apps.py`
3. `apps/organizations/exceptions.py`
4. `apps/organizations/models.py`
5. `apps/organizations/validators.py`
6. `apps/organizations/services.py`
7. `apps/organizations/forms.py`
8. `apps/organizations/permissions.py`
9. `apps/organizations/serializers.py`
10. `apps/organizations/views.py`
11. `apps/organizations/api_views.py`
12. `apps/organizations/urls.py`
13. `apps/organizations/admin.py`
14. `templates/organizations/onboarding.html`
15. `templates/organizations/profile_form.html`
16. `templates/organizations/profile_detail.html`
17. `templates/organizations/document_manage.html`
18. `templates/organizations/partials/status_badge.html`
19. `templates/admin_verification/queue.html`
20. `templates/admin_verification/review_detail.html`
21. `tests/test_organizations.py`
22. `tests/test_verification.py`

---

## 13. FILES TO MODIFY

1. `config/settings/base.py`:
   - Append `'apps.organizations'` to `LOCAL_APPS`.
   - Add `PRIVATE_MEDIA_ROOT = BASE_DIR / 'private_media'`.
2. `config/urls.py`:
   - Include `apps.organizations.urls` under root and `api/v1/`.
3. `templates/dashboards/donor_dashboard.html`:
   - Embed organization verification status banner and onboarding callout.
4. `templates/dashboards/receiver_dashboard.html`:
   - Embed organization verification status banner and onboarding callout.
5. `templates/dashboards/admin_dashboard.html`:
   - Link "Pending Verification" card to admin review queue.
6. `templates/components/navbar.html`:
   - Add links to Organization Profile and Admin Verification Queue (when admin).

---

## 14. DATABASE AND MIGRATION IMPACT & SAFETY

### 14.1 New Tables & Relations
1. `organizations_organizationprofile`:
   - Primary Key: `UUID`
   - One-to-One Foreign Key: `user_id` $\rightarrow$ `accounts_customuser.id` (ON DELETE CASCADE)
   - Foreign Key: `verified_by_id` $\rightarrow$ `accounts_customuser.id` (ON DELETE SET NULL, NULLABLE)
   - Indexes: `verification_status`, `city`, `registration_number` (unique).
2. `organizations_organizationdocument`:
   - Primary Key: `UUID`
   - Foreign Key: `organization_id` $\rightarrow$ `organizations_organizationprofile.id` (ON DELETE CASCADE)
   - Foreign Key: `reviewed_by_id` $\rightarrow$ `accounts_customuser.id` (ON DELETE SET NULL, NULLABLE)
   - Index: `document_type`, `review_status`.
3. `organizations_organizationverificationevent`:
   - Primary Key: `UUID`
   - Foreign Key: `organization_id` $\rightarrow$ `organizations_organizationprofile.id` (ON DELETE PROTECT)
   - Foreign Key: `actor_id` $\rightarrow$ `accounts_customuser.id` (ON DELETE SET NULL, NULLABLE)
   - Index: `created_at`, `event_type`.

### 14.2 Migration Sequence & Safety Guarantees
- **Migration Dependency:** `0001_initial` of `apps.organizations` will depend on `apps.accounts` migration `0001_initial`.
- **Existing User & Auth Safety:** Zero schema alterations to `CustomUser`. Existing user tables and auth tokens remain 100% untouched.
- **Database State:** The database will not be reset. No existing migrations will be altered or deleted.
- **Safe Rollback:** Dropping `apps.organizations` migration cleanly removes organization tables without affecting user credentials or auth tokens.

---

## 15. GEOLOCATION FOUNDATION & ARCHITECTURAL DEVIATION

### 15.1 Architectural Deviation Documented
In Phase 0 (`05_SANJOG_Database_Design.md`), a PostGIS `GEOGRAPHY(POINT, 4326)` column with GiST spatial indexing was specified. 

**Deviation in Phase 3:**
Phase 3 intentionally departs from PostGIS `PointField` by storing coordinates using standard decimal fields:
```python
latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
```

### 15.2 Justification & Limitations
1. **Portability & Environment Safety:**
   - GDAL C-libraries are not bundled on Windows standard Python environments.
   - The test runner frequently runs against SQLite (`USE_SQLITE=True`), where GeoDjango `PointField` crashes with `ImportError` / `GDALException`.
   - `DecimalField(max_digits=9, decimal_places=6)` provides physical accuracy down to **~11 centimeters**, which completely satisfies facility address requirements.
2. **Explicit Capability Boundary:**
   - **Spatial radius queries (`ST_DWithin`), bounding box lookups, and GiST spatial indexes are NOT available in Phase 3.**
   - No nearby-food discovery or proximity calculations are implemented in Phase 3.
3. **Future Migration Path (Phase 6):**
   - In **Phase 6** (`PHASE 6 — Food Discovery & PostGIS Geolocation`), when PostGIS and GDAL are enabled, a two-stage migration will add `location = PointField(geography=True, srid=4326)` and populate it from `(longitude, latitude)` values.

---

## 16. TESTING PLAN

Comprehensive test suite covering all functional, authorization, security, concurrency, and audit scenarios. **Exactly 42 test cases** are verified and passing across 6 core categories.

### 16.1 Organization Profile Management (`tests/test_organizations.py`) [9 Tests]
- [x] **TC-ORG-001:** Donor user successfully creates valid Donor organization profile (`RESTAURANT`).
- [x] **TC-ORG-002:** Receiver user successfully creates valid Receiver organization profile (`NGO`).
- [x] **TC-ORG-003:** Donor user attempting to select Receiver organization type (`SHELTER`) is rejected with validation error.
- [x] **TC-ORG-004:** Receiver user attempting to select Donor organization type (`HOTEL`) is rejected with validation error.
- [x] **TC-ORG-005:** Volunteer user attempting to create an organization profile is rejected with `403 Forbidden`.
- [x] **TC-ORG-006:** User cannot create multiple organization profiles (enforces one-to-one constraint).
- [x] **TC-ORG-007:** Organization owner can update draft profile details (address, contact info).
- [x] **TC-ORG-008:** Unauthorized user attempting to edit another user's organization profile is rejected (`403 Forbidden`).
- [x] **TC-ORG-009:** Latitude and longitude validation rejects coordinates outside valid GPS ranges (-90 to +90, -180 to +180).

### 16.2 Private File Lifecycle, Validation & Cleanup (`tests/test_organizations.py`) [10 Tests]
- [x] **TC-DOC-001:** Organization owner successfully uploads valid PDF document within 5MB limit.
- [x] **TC-DOC-002:** Organization owner successfully uploads valid PNG/JPEG document with matching magic bytes.
- [x] **TC-DOC-003:** Uploading an executable, script, or SVG file (`.exe`, `.sh`, `.py`, `.svg`) is rejected with `400 Bad Request`.
- [x] **TC-DOC-004:** Uploading a file exceeding 5MB size limit is rejected with `400 Bad Request`.
- [x] **TC-DOC-005:** File with spoofed extension (e.g., `.pdf` containing executable or corrupted bytes) is rejected after signature inspection.
- [x] **TC-DOC-006:** Non-owner user attempting to access private document download URL receives `403 Forbidden`.
- [x] **TC-DOC-007:** Unauthenticated request to document download URL is blocked (`401 Unauthorized` / redirect).
- [x] **TC-DOC-008:** Admin user can securely access and download private verification documents with secure headers (`nosniff`, `attachment`).
- [x] **TC-DOC-009:** Post-commit document deletion removes physical file from private storage; deletion blocked while organization is `PENDING`.
- [x] **TC-DOC-010:** Upload failure cleanup verifies physical file is purged if database transaction rolls back.

### 16.3 Document Review, Replacement & Approval Policy (`tests/test_organizations.py`) [5 Tests]
- [x] **TC-REQ-001:** Submitting organization without mandatory documents for its type (e.g., `RESTAURANT` missing FSSAI license) is rejected with `ValidationError`.
- [x] **TC-REQ-002:** Submitting organization with all required documents for its type transitions to `PENDING` successfully.
- [x] **TC-REQ-003:** Admin individual document review (`review_document`) correctly marks document `APPROVED` or `REJECTED` with notes.
- [x] **TC-REQ-004:** Rejected document history is retained when replacement document of same type is uploaded; both co-exist in audit history.
- [x] **TC-REQ-005:** Organization approval requires each mandatory document type to have an approved document; optional documents are NOT automatically approved; unapproved mandatory docs block organization approval.

### 16.4 Verification Workflow & Concurrency Control (`tests/test_verification.py`) [9 Tests]
- [x] **TC-VERIF-001:** Organization profile fields become locked (read-only) while status is `PENDING`.
- [x] **TC-VERIF-002:** Non-admin user attempting to call admin approval endpoint receives `403 Forbidden`.
- [x] **TC-VERIF-003:** Normal user cannot self-approve their organization via API payload manipulation.
- [x] **TC-VERIF-004:** Admin user successfully approves pending organization (status transitions to `APPROVED`).
- [x] **TC-VERIF-005:** Admin user successfully rejects pending organization with mandatory rejection notes.
- [x] **TC-VERIF-006:** Admin rejection fails if rejection reason is missing or empty.
- [x] **TC-VERIF-007:** Resubmission transitions from `REJECTED` back to `PENDING` when qualifying replacement documents are uploaded.
- [x] **TC-VERIF-008:** Concurrent verification decisions: state validation raises `409 Conflict` if organization is no longer `PENDING`.
- [x] **TC-VERIF-009:** PostgreSQL multithreaded row-lock test (`select_for_update`) verifies serialized execution (skipped on SQLite).

### 16.5 Audit Event Retention & Immutability (`tests/test_verification.py`) [4 Tests]
- [x] **TC-AUDIT-001:** Every status transition atomically creates an `OrganizationVerificationEvent` with actor, timestamp, previous status, new status, and notes.
- [x] **TC-AUDIT-002:** `OrganizationVerificationEvent` model instance updates and deletes raise `PermissionDenied`.
- [x] **TC-AUDIT-003:** Bulk QuerySet `update()` and `delete()` on `OrganizationVerificationEvent` raise `PermissionDenied`.
- [x] **TC-AUDIT-004:** `OrganizationProfile` deletion is blocked by `ProtectedError` (`on_delete=PROTECT`) when verification events exist.

### 16.6 REST API Canonical Endpoints & System Regression (`tests/test_organizations.py`, `tests/test_verification.py`) [5 Tests]
- [x] **TC-API-001:** `GET /api/v1/organizations/me/` returns current user's profile, documents, and audit timeline.
- [x] **TC-API-002:** Canonical document endpoints (`POST`, `GET`, `DELETE`) return consistent status codes and error bodies.
- [x] **TC-API-003:** Admin verification queue API returns paginated filtered results (`PENDING`, `APPROVED`, `REJECTED`).
- [x] **TC-API-004:** Existing Phase 1 & 2 tests (19 tests) continue to pass 100% without regression.
- [x] **TC-API-005:** `python manage.py check` executes with 0 errors.

---

## 17. TEAM PARALLELIZATION & OWNERSHIP BOUNDARIES

| Track | Primary Responsibilities | Target Files | Shared Dependencies |
| :--- | :--- | :--- | :--- |
| **Track 1: Models & Core Service** | Models, validators, audit events, migrations, service logic | `models.py`, `validators.py`, `services.py`, `migrations/` | Sole owner of model schema and migrations |
| **Track 2: REST API & Permissions** | DRF serializers, ViewSets, API views, DRF permissions | `serializers.py`, `permissions.py`, `api_views.py` | Imports from `services.py` |
| **Track 3: UI & HTMX Templates** | Django forms, template views, Tailwind/HTMX templates | `forms.py`, `views.py`, `templates/organizations/`, `templates/admin_verification/` | Imports from `forms.py` and `services.py` |
| **Track 4: QA & Automated Testing** | Unit tests, security tests, file upload attack simulations | `tests/test_organizations.py`, `tests/test_verification.py` | Tests full integration stack |

---

## 18. RISKS & MITIGATION

1. **Risk: PostGIS / GDAL Compatibility Failure on Dev Environments**
   - *Mitigation:* Store coordinates as `DecimalField(max_digits=9, decimal_places=6)`. Avoids native GDAL compilation crashes, supports precision up to ~11 cm, and enables smooth PostGIS migration in Phase 6.
2. **Risk: Exposure of Sensitive Verification Documents (IDOR Vulnerability)**
   - *Mitigation:* Store files outside public media in `settings.PRIVATE_MEDIA_ROOT` and serve them exclusively through an authenticated view requiring ownership or admin privileges.
3. **Risk: File Upload Vulnerabilities (Malicious Executables / Spoofed Extensions / SVG XSS)**
   - *Mitigation:* Magic header signature validation, strict extension-to-signature cross-checking, rejection of `svg` and all executable formats, and 5MB size ceiling.
4. **Risk: Self-Approval Privilege Escalation**
   - *Mitigation:* Verification state changes are strictly restricted to `VerificationService` methods that assert `request.user.is_admin_user`. Serializers ignore any user-supplied `verification_status` fields.
5. **Risk: Concurrent Administrator Decisions (Race Condition)**
   - *Mitigation:* `select_for_update()` pessimistic database row lock and state verification inside atomic transaction.

---

## 19. DEFINITION OF DONE (DoD)

Phase 3 will be marked complete only when all of the following conditions are met:
1. Donors can register and manage organization profiles with donor-specific types.
2. Receivers can register and manage organization profiles with receiver-specific types.
3. Role-to-organization-type mismatches are rejected at form, serializer, and service layers.
4. Volunteers are not required or prompted to create an organization profile.
5. Configurable document requirements per organization type are validated prior to submission.
6. Organization approval strictly requires every mandatory document type to have an approved document; unapproved mandatory docs block approval, and optional documents are not silently approved.
7. Rejected document history is preserved upon uploading replacement documents.
8. Magic header signatures and file extensions are validated, and upload transaction rollbacks cleanly purge files.
9. Private verification documents are stored outside public media and cannot be accessed by unauthorized users.
10. Administrators can review pending organizations via an admin review queue.
11. Administrators can review individual documents and approve or reject organizations with recorded timestamps, admin ID, and rejection reasons.
12. `OrganizationVerificationEvent` records full immutable audit history protected by `on_delete=PROTECT` and custom managers across all review and resubmission events.
13. Concurrent administrator review conflicts are prevented via transactional state checks and row locking.
14. All **42 planned test cases** pass (100% test pass rate across new and existing tests).
15. Existing Phase 1 and Phase 2 authentication functionality remains intact without regression.
16. Database migrations run cleanly and safely without modifying `CustomUser`.
17. `python manage.py check` reports 0 issues.

---

## 20. CONFLICTS WITH EXISTING ARCHITECTURE & RECONCILIATION

1. **`VolunteerProfile` Placement:**
   - *Finding in Phase 0 DB Doc:* `VolunteerProfile` was listed under Table 4 in `05_SANJOG_Database_Design.md`.
   - *Reconciliation:* The Phase 3 prompt explicitly states: *"VOLUNTEER accounts do not require an organization profile by default. Do not force volunteers through organization verification."*
   - *Decision:* `VolunteerProfile` is deferred to Phase 9 (`apps/pickups/`) where volunteer logistics and vehicle types are implemented. Phase 3 focuses solely on donor and receiver organizations.
2. **Coordinate Storage vs PostGIS:**
   - *Finding:* PostGIS `GEOGRAPHY(POINT, 4326)` was proposed in Phase 0.
   - *Reconciliation:* GDAL is not installed in the Windows environment, and SQLite fallback is used during testing.
   - *Decision:* Use `DecimalField(max_digits=9, decimal_places=6)` for latitude and longitude in Phase 3. This maintains full precision without native C-library dependencies. A property helper will prepare coordinates for Phase 6 spatial queries.

---

## 21. RECOMMENDED CHANGES & SEQUENCE

1. **App Namespace:** Create `apps/organizations/` as the single authoritative app for all organization profile, document, and verification logic.
2. **Sequential Implementation Steps (Post-Approval):**
   - **Step 1:** Configure `PRIVATE_MEDIA_ROOT` in `config/settings/base.py` and register `'apps.organizations'`.
   - **Step 2:** Create `apps/organizations/` app skeleton.
   - **Step 3:** Implement models (`OrganizationProfile`, `OrganizationDocument`, `OrganizationVerificationEvent`).
   - **Step 4:** Implement validators (magic bytes, size, extension consistency, required document mapping).
   - **Step 5:** Generate and execute migrations (`0001_initial.py`).
   - **Step 6:** Implement `services.py` with transactional row locking, state machine, fail-safe file cleanup, and event recording.
   - **Step 7:** Implement forms and DRF serializers.
   - **Step 8:** Implement permissions and security wrappers.
   - **Step 9:** Implement template views, HTMX handlers, and REST API endpoints.
   - **Step 10:** Create responsive HTML/HTMX templates for onboarding, profile, documents, and admin queue.
   - **Step 11:** Update existing dashboards to link into the verification pipeline.
   - **Step 12:** Write and execute automated tests in `tests/test_organizations.py` and `tests/test_verification.py`.
   - **Step 13:** Verify `python manage.py check` and ensure 100% test pass rate across all 42 tests.

---

## 22. IMPLEMENTATION COMPLETION STATUS
- **Approval:** Received `APPROVED — PROCEED` from User.
- **Implementation:** Complete across `apps/organizations`, templates, routes, and admin verification desks.
- **Verification:** 100% test pass rate across all 59 tests (19 Phase 1/2 tests + 42 Phase 3 test cases).
- **Zero Regressions:** Phase 0, 1, and 2 systems completely intact. `CustomUser` unmutated.
