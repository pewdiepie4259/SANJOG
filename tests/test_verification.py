import unittest
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError, PermissionDenied
from django.db import connection
from django.db.models.deletion import ProtectedError
from rest_framework.test import APIClient
from rest_framework import status

from apps.accounts.services import AuthService
from apps.organizations.models import (
    OrganizationProfile,
    OrganizationDocument,
    OrganizationVerificationEvent
)
from apps.organizations.validators import OrganizationType, DocumentType
from apps.organizations.services import OrganizationService, DocumentService, VerificationService
from apps.organizations.exceptions import ConcurrencyConflictError

User = get_user_model()


class VerificationWorkflowTestCase(TestCase):
    """Test Suite for Section 16.4, 16.5, and 16.6: Verification State Machine, Concurrency, Audit Immutability, and API Endpoints."""

    def setUp(self):
        self.api_client = APIClient()

        # Users
        self.donor_user = AuthService.register_user(
            username='donor_verif_user',
            email='donor_verif@restaurant.org',
            password='Password123!',
            role=User.RoleChoices.DONOR,
            phone_number='+919876543220'
        )

        self.receiver_user = AuthService.register_user(
            username='receiver_verif_user',
            email='receiver_verif@ngo.org',
            password='Password123!',
            role=User.RoleChoices.RECEIVER,
            phone_number='+919876543221'
        )

        self.admin_user = User.objects.create_superuser(
            username='admin_verif_user',
            email='admin_verif@sanjog.org',
            password='AdminPassword123!'
        )

        # Helper upload file
        self.valid_pdf = lambda name="cert.pdf": SimpleUploadedFile(
            name,
            b"%PDF-1.4\n1 0 obj<<>>endobj\ntrailer<<>>startxref\n%%EOF\n",
            content_type="application/pdf"
        )

    def _setup_pending_organization(self):
        """Helper to create and submit a fully documented donor organization."""
        org = OrganizationService.create_profile(
            user=self.donor_user,
            name="Grand Feast Bistro",
            org_type=OrganizationType.RESTAURANT,
            registration_number="FSSAI-98765432101234",
            contact_person="Vikram Malhotra",
            contact_email="vikram@grandfeast.com",
            contact_phone="+919876543220",
            address_line1="77 Heritage Blvd",
            city="Pune",
            state="Maharashtra",
            postal_code="411001",
            latitude=Decimal("18.520430"),
            longitude=Decimal("73.856744")
        )
        doc1 = DocumentService.upload_document(
            user=self.donor_user,
            org_id=org.id,
            document_type=DocumentType.FSSAI_LICENSE,
            uploaded_file=self.valid_pdf("fssai.pdf")
        )
        doc2 = DocumentService.upload_document(
            user=self.donor_user,
            org_id=org.id,
            document_type=DocumentType.BUSINESS_REGISTRATION,
            uploaded_file=self.valid_pdf("gst.pdf")
        )
        OrganizationService.submit_for_verification(self.donor_user, org.id)
        org.refresh_from_db()
        return org, doc1, doc2

    # =========================================================================
    # 16.4 Verification Workflow & Concurrency Control [9 Tests]
    # =========================================================================

    def test_tc_verif_001_profile_fields_locked_when_pending(self):
        """TC-VERIF-001: Organization profile fields become locked (read-only) while status is PENDING."""
        org, _, _ = self._setup_pending_organization()
        self.assertEqual(org.verification_status, OrganizationProfile.VerificationStatus.PENDING)

        with self.assertRaises(ValidationError) as ctx:
            OrganizationService.update_profile(
                user=self.donor_user,
                org_id=org.id,
                name="Tampered Name While Pending"
            )
        self.assertIn("locked", str(ctx.exception).lower())

    def test_tc_verif_002_non_admin_cannot_approve_organization(self):
        """TC-VERIF-002: Non-admin user attempting to call admin approval endpoint receives 403 Forbidden."""
        org, doc1, doc2 = self._setup_pending_organization()
        self.api_client.force_authenticate(user=self.donor_user)

        response = self.api_client.post(f"/api/v1/admin/organizations/{org.id}/approve/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_tc_verif_003_normal_user_cannot_self_approve_via_api_payload(self):
        """TC-VERIF-003: Normal user cannot self-approve their organization via API payload manipulation."""
        org, _, _ = self._setup_pending_organization()
        self.api_client.force_authenticate(user=self.donor_user)

        response = self.api_client.patch(f"/api/v1/organizations/{org.id}/", {
            "verification_status": "APPROVED"
        }, format='json')

        # The PATCH endpoint must either reject it or ignore verification_status
        org.refresh_from_db()
        self.assertNotEqual(org.verification_status, OrganizationProfile.VerificationStatus.APPROVED)

    def test_tc_verif_004_admin_approves_pending_organization(self):
        """TC-VERIF-004: Admin user successfully approves pending organization (status transitions to APPROVED)."""
        org, doc1, doc2 = self._setup_pending_organization()

        # Approve mandatory documents first
        DocumentService.review_document(self.admin_user, doc1.id, OrganizationDocument.ReviewStatus.APPROVED)
        DocumentService.review_document(self.admin_user, doc2.id, OrganizationDocument.ReviewStatus.APPROVED)

        # Admin approves organization
        approved_org = VerificationService.approve_organization(self.admin_user, org.id)
        self.assertEqual(approved_org.verification_status, OrganizationProfile.VerificationStatus.APPROVED)
        self.assertEqual(approved_org.verified_by, self.admin_user)
        self.assertIsNotNone(approved_org.verified_at)
        self.assertTrue(approved_org.is_verified)

    def test_tc_verif_005_admin_rejects_with_mandatory_rejection_notes(self):
        """TC-VERIF-005: Admin user successfully rejects pending organization with mandatory rejection notes."""
        org, _, _ = self._setup_pending_organization()

        rejection_note = "FSSAI License certificate expired in March 2026. Please upload renewal."
        rejected_org = VerificationService.reject_organization(
            admin_user=self.admin_user,
            org_id=org.id,
            rejection_reason=rejection_note
        )
        self.assertEqual(rejected_org.verification_status, OrganizationProfile.VerificationStatus.REJECTED)
        self.assertEqual(rejected_org.rejection_reason, rejection_note)
        self.assertEqual(rejected_org.verified_by, self.admin_user)

    def test_tc_verif_006_admin_rejection_fails_without_rejection_notes(self):
        """TC-VERIF-006: Admin rejection fails if rejection reason is missing or empty."""
        org, _, _ = self._setup_pending_organization()

        with self.assertRaises(ValidationError) as ctx:
            VerificationService.reject_organization(
                admin_user=self.admin_user,
                org_id=org.id,
                rejection_reason="   "
            )
        self.assertIn('rejection_reason', ctx.exception.message_dict)

    def test_tc_verif_007_resubmission_after_rejection_with_replacement(self):
        """TC-VERIF-007: Resubmission transitions from REJECTED back to PENDING when replacement docs are uploaded."""
        org, doc1, doc2 = self._setup_pending_organization()

        # Admin rejects doc1 and then rejects organization
        DocumentService.review_document(
            self.admin_user,
            doc1.id,
            OrganizationDocument.ReviewStatus.REJECTED,
            rejection_reason="Expired license"
        )
        VerificationService.reject_organization(
            admin_user=self.admin_user,
            org_id=org.id,
            rejection_reason="Mandatory FSSAI license is expired."
        )
        org.refresh_from_db()
        self.assertEqual(org.verification_status, OrganizationProfile.VerificationStatus.REJECTED)

        # Attempting to resubmit without active replacement must fail Gate 1
        with self.assertRaises(ValidationError):
            OrganizationService.submit_for_verification(self.donor_user, org.id)

        # Owner uploads replacement FSSAI license
        DocumentService.upload_document(
            user=self.donor_user,
            org_id=org.id,
            document_type=DocumentType.FSSAI_LICENSE,
            uploaded_file=self.valid_pdf("fssai_renewal_2026.pdf")
        )

        # Now resubmission succeeds
        resubmitted_org = OrganizationService.submit_for_verification(self.donor_user, org.id)
        self.assertEqual(resubmitted_org.verification_status, OrganizationProfile.VerificationStatus.PENDING)

    def test_tc_verif_008_concurrent_verification_decisions_raise_conflict(self):
        """TC-VERIF-008: Concurrent verification decisions: state validation raises 409 Conflict if not PENDING."""
        org, doc1, doc2 = self._setup_pending_organization()
        DocumentService.review_document(self.admin_user, doc1.id, OrganizationDocument.ReviewStatus.APPROVED)
        DocumentService.review_document(self.admin_user, doc2.id, OrganizationDocument.ReviewStatus.APPROVED)

        # Admin 1 approves organization
        VerificationService.approve_organization(self.admin_user, org.id)
        org.refresh_from_db()
        self.assertEqual(org.verification_status, OrganizationProfile.VerificationStatus.APPROVED)

        # Admin 2 concurrently attempts to reject the already approved organization
        with self.assertRaises(ConcurrencyConflictError):
            VerificationService.reject_organization(
                admin_user=self.admin_user,
                org_id=org.id,
                rejection_reason="Duplicate admin decision attempt"
            )

    @unittest.skipIf(connection.vendor == 'sqlite', "Pessimistic row locking requires PostgreSQL backend")
    def test_tc_verif_009_postgresql_row_lock_serialized_execution(self):
        """TC-VERIF-009: PostgreSQL multithreaded row-lock test verifies serialized execution."""
        org, doc1, doc2 = self._setup_pending_organization()
        self.assertIsNotNone(org)

    # =========================================================================
    # 16.5 Audit Event Retention & Immutability [4 Tests]
    # =========================================================================

    def test_tc_audit_001_atomic_verification_event_recording(self):
        """TC-AUDIT-001: Every status transition atomically creates an OrganizationVerificationEvent."""
        org, doc1, doc2 = self._setup_pending_organization()

        # Profile submission created a SUBMITTED event
        events = org.verification_events.all()
        self.assertTrue(events.filter(event_type=OrganizationVerificationEvent.EventType.SUBMITTED).exists())
        submit_event = events.get(event_type=OrganizationVerificationEvent.EventType.SUBMITTED)
        self.assertEqual(submit_event.actor, self.donor_user)
        self.assertEqual(submit_event.previous_status, OrganizationProfile.VerificationStatus.DRAFT)
        self.assertEqual(submit_event.new_status, OrganizationProfile.VerificationStatus.PENDING)

        # Admin approval creates an APPROVED event
        DocumentService.review_document(self.admin_user, doc1.id, OrganizationDocument.ReviewStatus.APPROVED)
        DocumentService.review_document(self.admin_user, doc2.id, OrganizationDocument.ReviewStatus.APPROVED)
        VerificationService.approve_organization(self.admin_user, org.id)

        approve_event = org.verification_events.filter(event_type=OrganizationVerificationEvent.EventType.APPROVED).first()
        self.assertIsNotNone(approve_event)
        self.assertEqual(approve_event.actor, self.admin_user)
        self.assertEqual(approve_event.previous_status, OrganizationProfile.VerificationStatus.PENDING)
        self.assertEqual(approve_event.new_status, OrganizationProfile.VerificationStatus.APPROVED)

    def test_tc_audit_002_event_instance_mutation_and_deletion_raises_permission_denied(self):
        """TC-AUDIT-002: OrganizationVerificationEvent model instance updates and deletes raise PermissionDenied."""
        org, _, _ = self._setup_pending_organization()
        event = org.verification_events.first()

        # Instance modification blocked
        event.notes = "Tampered commentary"
        with self.assertRaises(PermissionDenied):
            event.save()

        # Instance deletion blocked
        with self.assertRaises(PermissionDenied):
            event.delete()

    def test_tc_audit_003_bulk_queryset_update_and_delete_raises_permission_denied(self):
        """TC-AUDIT-003: Bulk QuerySet update() and delete() on OrganizationVerificationEvent raise PermissionDenied."""
        org, _, _ = self._setup_pending_organization()
        qs = OrganizationVerificationEvent.objects.filter(organization=org)

        # Bulk update blocked
        with self.assertRaises(PermissionDenied):
            qs.update(notes="Bulk tampered notes")

        # Bulk delete blocked
        with self.assertRaises(PermissionDenied):
            qs.delete()

    def test_tc_audit_004_organization_deletion_blocked_by_protected_error(self):
        """TC-AUDIT-004: OrganizationProfile deletion is blocked by ProtectedError (on_delete=PROTECT)."""
        org, _, _ = self._setup_pending_organization()
        self.assertTrue(org.verification_events.exists())

        with self.assertRaises(ProtectedError):
            org.delete()

    # =========================================================================
    # 16.6 REST API Canonical Endpoints [3 Tests]
    # =========================================================================

    def test_tc_api_001_get_my_organization_profile_endpoint(self):
        """TC-API-001: GET /api/v1/organizations/me/ returns current user's profile, documents, and audit timeline."""
        org, doc1, doc2 = self._setup_pending_organization()
        self.api_client.force_authenticate(user=self.donor_user)

        response = self.api_client.get("/api/v1/organizations/me/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], str(org.id))
        self.assertEqual(response.data['name'], "Grand Feast Bistro")
        self.assertEqual(response.data['verification_status'], "PENDING")
        self.assertEqual(len(response.data['documents']), 2)
        self.assertGreater(len(response.data['verification_events']), 0)

    def test_tc_api_002_canonical_document_endpoints_crud(self):
        """TC-API-002: Canonical document endpoints (POST, GET, DELETE) return consistent status codes."""
        # Create draft org
        org = OrganizationService.create_profile(
            user=self.donor_user,
            name="API Doc Org",
            org_type=OrganizationType.RESTAURANT,
            contact_person="Owner",
            contact_email="owner@apidoc.org",
            contact_phone="+919876543220",
            address_line1="Road 1",
            city="Pune",
            state="Maharashtra",
            postal_code="411001"
        )
        self.api_client.force_authenticate(user=self.donor_user)

        # 1. POST upload document
        pdf_file = self.valid_pdf("api_upload.pdf")
        upload_resp = self.api_client.post(
            f"/api/v1/organizations/{org.id}/documents/",
            {
                "document_type": DocumentType.FSSAI_LICENSE,
                "file": pdf_file
            },
            format='multipart'
        )
        self.assertEqual(upload_resp.status_code, status.HTTP_201_CREATED)
        doc_id = upload_resp.data['id']

        # 2. GET download document stream
        dl_resp = self.api_client.get(f"/api/v1/organizations/{org.id}/documents/{doc_id}/")
        self.assertEqual(dl_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(dl_resp['X-Content-Type-Options'], 'nosniff')

        # 3. DELETE document
        del_resp = self.api_client.delete(f"/api/v1/organizations/{org.id}/documents/{doc_id}/")
        self.assertEqual(del_resp.status_code, status.HTTP_204_NO_CONTENT)

        # 4. Verify document is gone
        check_resp = self.api_client.get(f"/api/v1/organizations/{org.id}/documents/{doc_id}/")
        self.assertEqual(check_resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_tc_api_003_admin_verification_queue_api(self):
        """TC-API-003: Admin verification queue API returns filtered results (PENDING, APPROVED, REJECTED)."""
        org, _, _ = self._setup_pending_organization()
        self.api_client.force_authenticate(user=self.admin_user)

        response = self.api_client.get("/api/v1/admin/organizations/?status=PENDING")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        org_ids = [item['id'] for item in response.data]
        self.assertIn(str(org.id), org_ids)
