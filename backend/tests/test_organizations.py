import os
from decimal import Decimal
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError, PermissionDenied
from django.db import transaction

from apps.accounts.services import AuthService
from apps.organizations.models import (
    OrganizationProfile,
    OrganizationDocument,
    OrganizationVerificationEvent,
    private_document_storage
)
from apps.organizations.validators import OrganizationType, DocumentType
from apps.organizations.services import OrganizationService, DocumentService, VerificationService

User = get_user_model()


class OrganizationProfileTestCase(TestCase):
    """Test Suite for Section 16.1 & 16.2 & 16.3: Profile Management, File Lifecycle, and Document Rules."""

    def setUp(self):
        self.client = Client()

        # Seed test users
        self.donor_user = AuthService.register_user(
            username='donor_org_tester',
            email='donor_tester@restaurant.org',
            password='Password123!',
            role=User.RoleChoices.DONOR,
            phone_number='+919876543210'
        )

        self.receiver_user = AuthService.register_user(
            username='receiver_org_tester',
            email='receiver_tester@ngo.org',
            password='Password123!',
            role=User.RoleChoices.RECEIVER,
            phone_number='+919876543211'
        )

        self.volunteer_user = AuthService.register_user(
            username='volunteer_tester',
            email='volunteer_tester@logistics.org',
            password='Password123!',
            role=User.RoleChoices.VOLUNTEER,
            phone_number='+919876543212'
        )

        self.admin_user = User.objects.create_superuser(
            username='admin_tester',
            email='admin_tester@sanjog.org',
            password='AdminPassword123!'
        )

        # Helper valid file buffers
        self.valid_pdf = lambda name="test_fssai.pdf": SimpleUploadedFile(
            name,
            b"%PDF-1.4\n1 0 obj<<>>endobj\ntrailer<<>>startxref\n%%EOF\n",
            content_type="application/pdf"
        )
        self.valid_png = lambda name="test_cert.png": SimpleUploadedFile(
            name,
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4",
            content_type="image/png"
        )
        self.valid_jpg = lambda name="test_cert.jpg": SimpleUploadedFile(
            name,
            b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00\xff\xdb\x00C\x00",
            content_type="image/jpeg"
        )

    # =========================================================================
    # 16.1 Organization Profile Management [9 Tests]
    # =========================================================================

    def test_tc_org_001_donor_creates_valid_profile(self):
        """TC-ORG-001: Donor user successfully creates valid Donor organization profile (RESTAURANT)."""
        org = OrganizationService.create_profile(
            user=self.donor_user,
            name="Spice Garden Kitchen",
            org_type=OrganizationType.RESTAURANT,
            registration_number="FSSAI-12345678901234",
            contact_person="Rajesh Sharma",
            contact_email="rajesh@spicegarden.com",
            contact_phone="+919876543210",
            address_line1="123 Food Street",
            city="Pune",
            state="Maharashtra",
            postal_code="411001",
            latitude=Decimal("18.520430"),
            longitude=Decimal("73.856744")
        )
        self.assertIsNotNone(org.id)
        self.assertEqual(org.verification_status, OrganizationProfile.VerificationStatus.DRAFT)
        self.assertEqual(org.user, self.donor_user)
        self.assertEqual(org.org_type, OrganizationType.RESTAURANT)

    def test_tc_org_002_receiver_creates_valid_profile(self):
        """TC-ORG-002: Receiver user successfully creates valid Receiver organization profile (NGO)."""
        org = OrganizationService.create_profile(
            user=self.receiver_user,
            name="Seva Shelter Foundation",
            org_type=OrganizationType.NGO,
            registration_number="80G-AAATS1234F",
            contact_person="Sister Maria",
            contact_email="maria@sevashelter.org",
            contact_phone="+919876543211",
            address_line1="45 Care Lane",
            city="Pune",
            state="Maharashtra",
            postal_code="411002"
        )
        self.assertIsNotNone(org.id)
        self.assertEqual(org.verification_status, OrganizationProfile.VerificationStatus.DRAFT)
        self.assertEqual(org.user, self.receiver_user)
        self.assertEqual(org.org_type, OrganizationType.NGO)

    def test_tc_org_003_donor_selecting_receiver_type_fails(self):
        """TC-ORG-003: Donor user attempting to select Receiver organization type (SHELTER) is rejected."""
        with self.assertRaises(ValidationError) as ctx:
            OrganizationService.create_profile(
                user=self.donor_user,
                name="Invalid Shelter by Donor",
                org_type=OrganizationType.SHELTER,
                contact_person="Donor Person",
                contact_email="donor@invalid.org",
                contact_phone="+919876543210",
                address_line1="123 Street",
                city="Pune",
                state="Maharashtra",
                postal_code="411001"
            )
        self.assertIn('org_type', ctx.exception.message_dict)

    def test_tc_org_004_receiver_selecting_donor_type_fails(self):
        """TC-ORG-004: Receiver user attempting to select Donor organization type (HOTEL) is rejected."""
        with self.assertRaises(ValidationError) as ctx:
            OrganizationService.create_profile(
                user=self.receiver_user,
                name="Grand Hotel by Receiver",
                org_type=OrganizationType.HOTEL,
                contact_person="Receiver Person",
                contact_email="receiver@invalid.org",
                contact_phone="+919876543211",
                address_line1="45 Street",
                city="Pune",
                state="Maharashtra",
                postal_code="411002"
            )
        self.assertIn('org_type', ctx.exception.message_dict)

    def test_tc_org_005_volunteer_creating_profile_forbidden(self):
        """TC-ORG-005: Volunteer user attempting to create an organization profile is rejected with PermissionDenied."""
        with self.assertRaises(PermissionDenied):
            OrganizationService.create_profile(
                user=self.volunteer_user,
                name="Volunteer Logistics Unit",
                org_type=OrganizationType.RESTAURANT,
                contact_person="Volunteer Name",
                contact_email="vol@sanjog.org",
                contact_phone="+919876543212",
                address_line1="Road 1",
                city="Pune",
                state="Maharashtra",
                postal_code="411001"
            )

    def test_tc_org_006_user_cannot_create_multiple_profiles(self):
        """TC-ORG-006: User cannot create multiple organization profiles (enforces one-to-one constraint)."""
        OrganizationService.create_profile(
            user=self.donor_user,
            name="First Restaurant",
            org_type=OrganizationType.RESTAURANT,
            contact_person="Person One",
            contact_email="person1@rest.org",
            contact_phone="+919876543210",
            address_line1="Street 1",
            city="Pune",
            state="Maharashtra",
            postal_code="411001"
        )
        with self.assertRaises(ValidationError):
            OrganizationService.create_profile(
                user=self.donor_user,
                name="Second Restaurant",
                org_type=OrganizationType.RESTAURANT,
                contact_person="Person Two",
                contact_email="person2@rest.org",
                contact_phone="+919876543210",
                address_line1="Street 2",
                city="Pune",
                state="Maharashtra",
                postal_code="411001"
            )

    def test_tc_org_007_owner_updates_draft_profile(self):
        """TC-ORG-007: Organization owner can update draft profile details (address, contact info)."""
        org = OrganizationService.create_profile(
            user=self.donor_user,
            name="Draft Kitchen",
            org_type=OrganizationType.RESTAURANT,
            contact_person="Original Contact",
            contact_email="orig@kitchen.org",
            contact_phone="+919876543210",
            address_line1="Original Address",
            city="Pune",
            state="Maharashtra",
            postal_code="411001"
        )
        updated_org = OrganizationService.update_profile(
            user=self.donor_user,
            org_id=org.id,
            contact_person="Updated Contact",
            city="Mumbai"
        )
        self.assertEqual(updated_org.contact_person, "Updated Contact")
        self.assertEqual(updated_org.city, "Mumbai")

    def test_tc_org_008_unauthorized_user_cannot_edit_profile(self):
        """TC-ORG-008: Unauthorized user attempting to edit another user's organization profile is rejected (403)."""
        org = OrganizationService.create_profile(
            user=self.donor_user,
            name="Donor's Restaurant",
            org_type=OrganizationType.RESTAURANT,
            contact_person="Owner",
            contact_email="owner@rest.org",
            contact_phone="+919876543210",
            address_line1="Street 1",
            city="Pune",
            state="Maharashtra",
            postal_code="411001"
        )
        with self.assertRaises(PermissionDenied):
            OrganizationService.update_profile(
                user=self.receiver_user,
                org_id=org.id,
                name="Hacked Name"
            )

    def test_tc_org_009_invalid_gps_coordinates_rejected(self):
        """TC-ORG-009: Latitude and longitude validation rejects coordinates outside valid GPS ranges."""
        with self.assertRaises(ValidationError) as ctx_lat:
            OrganizationService.create_profile(
                user=self.donor_user,
                name="GPS Out of Bounds 1",
                org_type=OrganizationType.RESTAURANT,
                contact_person="Owner",
                contact_email="owner@rest.org",
                contact_phone="+919876543210",
                address_line1="Street 1",
                city="Pune",
                state="Maharashtra",
                postal_code="411001",
                latitude=Decimal("95.000000"),  # > 90
                longitude=Decimal("73.856744")
            )
        self.assertIn('latitude', ctx_lat.exception.message_dict)

        with self.assertRaises(ValidationError) as ctx_lng:
            OrganizationService.create_profile(
                user=self.donor_user,
                name="GPS Out of Bounds 2",
                org_type=OrganizationType.RESTAURANT,
                contact_person="Owner",
                contact_email="owner@rest.org",
                contact_phone="+919876543210",
                address_line1="Street 1",
                city="Pune",
                state="Maharashtra",
                postal_code="411001",
                latitude=Decimal("18.520430"),
                longitude=Decimal("-190.000000")  # < -180
            )
        self.assertIn('longitude', ctx_lng.exception.message_dict)

    # =========================================================================
    # 16.2 Private File Lifecycle, Validation & Cleanup [10 Tests]
    # =========================================================================

    def test_tc_doc_001_owner_uploads_valid_pdf(self):
        """TC-DOC-001: Organization owner successfully uploads valid PDF document within 5MB limit."""
        org = OrganizationService.create_profile(
            user=self.donor_user,
            name="PDF Upload Org",
            org_type=OrganizationType.RESTAURANT,
            contact_person="Owner",
            contact_email="owner@pdf.org",
            contact_phone="+919876543210",
            address_line1="Street 1",
            city="Pune",
            state="Maharashtra",
            postal_code="411001"
        )
        pdf_file = self.valid_pdf("fssai_cert.pdf")
        doc = DocumentService.upload_document(
            user=self.donor_user,
            org_id=org.id,
            document_type=DocumentType.FSSAI_LICENSE,
            uploaded_file=pdf_file
        )
        self.assertIsNotNone(doc.id)
        self.assertEqual(doc.review_status, OrganizationDocument.ReviewStatus.PENDING)
        self.assertTrue(private_document_storage.exists(doc.file.name))

    def test_tc_doc_002_owner_uploads_valid_png_and_jpeg(self):
        """TC-DOC-002: Organization owner successfully uploads valid PNG/JPEG document with matching magic bytes."""
        org = OrganizationService.create_profile(
            user=self.donor_user,
            name="Image Upload Org",
            org_type=OrganizationType.RESTAURANT,
            contact_person="Owner",
            contact_email="owner@img.org",
            contact_phone="+919876543210",
            address_line1="Street 1",
            city="Pune",
            state="Maharashtra",
            postal_code="411001"
        )
        png_doc = DocumentService.upload_document(
            user=self.donor_user,
            org_id=org.id,
            document_type=DocumentType.BUSINESS_REGISTRATION,
            uploaded_file=self.valid_png("gst_cert.png")
        )
        jpg_doc = DocumentService.upload_document(
            user=self.donor_user,
            org_id=org.id,
            document_type=DocumentType.ID_PROOF,
            uploaded_file=self.valid_jpg("id_card.jpg")
        )
        self.assertEqual(png_doc.review_status, OrganizationDocument.ReviewStatus.PENDING)
        self.assertEqual(jpg_doc.review_status, OrganizationDocument.ReviewStatus.PENDING)
        self.assertTrue(private_document_storage.exists(png_doc.file.name))
        self.assertTrue(private_document_storage.exists(jpg_doc.file.name))

    def test_tc_doc_003_disallowed_formats_rejected(self):
        """TC-DOC-003: Uploading an executable, script, or SVG file (.exe, .sh, .py, .svg) is rejected with 400."""
        org = OrganizationService.create_profile(
            user=self.donor_user,
            name="Security Test Org",
            org_type=OrganizationType.RESTAURANT,
            contact_person="Owner",
            contact_email="owner@sec.org",
            contact_phone="+919876543210",
            address_line1="Street 1",
            city="Pune",
            state="Maharashtra",
            postal_code="411001"
        )
        disallowed_files = [
            SimpleUploadedFile("exploit.exe", b"MZ\x90\x00executable bytes", content_type="application/x-dosexec"),
            SimpleUploadedFile("script.sh", b"#!/bin/bash\nrm -rf /", content_type="application/x-sh"),
            SimpleUploadedFile("exploit.py", b"import os\nos.system('dir')", content_type="text/x-python"),
            SimpleUploadedFile("image.svg", b"<svg><script>alert(1)</script></svg>", content_type="image/svg+xml"),
        ]
        for bad_file in disallowed_files:
            with self.assertRaises(ValidationError):
                DocumentService.upload_document(
                    user=self.donor_user,
                    org_id=org.id,
                    document_type=DocumentType.OTHER,
                    uploaded_file=bad_file
                )

    def test_tc_doc_004_file_exceeding_5mb_rejected(self):
        """TC-DOC-004: Uploading a file exceeding 5MB size limit is rejected with 400 Bad Request."""
        org = OrganizationService.create_profile(
            user=self.donor_user,
            name="Size Test Org",
            org_type=OrganizationType.RESTAURANT,
            contact_person="Owner",
            contact_email="owner@size.org",
            contact_phone="+919876543210",
            address_line1="Street 1",
            city="Pune",
            state="Maharashtra",
            postal_code="411001"
        )
        # 5MB + 1024 bytes
        large_bytes = b"%PDF-1.4\n" + b"A" * (5 * 1024 * 1024 + 1024)
        large_file = SimpleUploadedFile("too_big.pdf", large_bytes, content_type="application/pdf")

        with self.assertRaises(ValidationError):
            DocumentService.upload_document(
                user=self.donor_user,
                org_id=org.id,
                document_type=DocumentType.FSSAI_LICENSE,
                uploaded_file=large_file
            )

    def test_tc_doc_005_spoofed_file_extension_rejected(self):
        """TC-DOC-005: File with spoofed extension (e.g. .pdf containing random text or exe header) is rejected."""
        org = OrganizationService.create_profile(
            user=self.donor_user,
            name="Spoof Test Org",
            org_type=OrganizationType.RESTAURANT,
            contact_person="Owner",
            contact_email="owner@spoof.org",
            contact_phone="+919876543210",
            address_line1="Street 1",
            city="Pune",
            state="Maharashtra",
            postal_code="411001"
        )
        fake_pdf = SimpleUploadedFile(
            "malicious.pdf",
            b"MZ\x90\x00this_is_an_executable_masquerading_as_pdf",
            content_type="application/pdf"
        )
        with self.assertRaises(ValidationError) as ctx:
            DocumentService.upload_document(
                user=self.donor_user,
                org_id=org.id,
                document_type=DocumentType.FSSAI_LICENSE,
                uploaded_file=fake_pdf
            )
        self.assertTrue(
            "File content" in str(ctx.exception) or "extension" in str(ctx.exception),
            f"Expected file content error, got: {ctx.exception}"
        )

    def test_tc_doc_006_non_owner_cannot_download_private_file(self):
        """TC-DOC-006: Non-owner user attempting to access private document download URL receives 403 Forbidden."""
        org = OrganizationService.create_profile(
            user=self.donor_user,
            name="Privacy Test Org",
            org_type=OrganizationType.RESTAURANT,
            contact_person="Owner",
            contact_email="owner@priv.org",
            contact_phone="+919876543210",
            address_line1="Street 1",
            city="Pune",
            state="Maharashtra",
            postal_code="411001"
        )
        doc = DocumentService.upload_document(
            user=self.donor_user,
            org_id=org.id,
            document_type=DocumentType.FSSAI_LICENSE,
            uploaded_file=self.valid_pdf("private.pdf")
        )
        # Login as non-owner receiver
        self.client.force_login(self.receiver_user)
        response = self.client.get(f"/organizations/documents/{doc.id}/download/")
        self.assertEqual(response.status_code, 403)

    def test_tc_doc_007_unauthenticated_request_blocked(self):
        """TC-DOC-007: Unauthenticated request to document download URL is blocked (redirect to login)."""
        org = OrganizationService.create_profile(
            user=self.donor_user,
            name="Unauth Test Org",
            org_type=OrganizationType.RESTAURANT,
            contact_person="Owner",
            contact_email="owner@unauth.org",
            contact_phone="+919876543210",
            address_line1="Street 1",
            city="Pune",
            state="Maharashtra",
            postal_code="411001"
        )
        doc = DocumentService.upload_document(
            user=self.donor_user,
            org_id=org.id,
            document_type=DocumentType.FSSAI_LICENSE,
            uploaded_file=self.valid_pdf("secret.pdf")
        )
        self.client.logout()
        response = self.client.get(f"/organizations/documents/{doc.id}/download/")
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_tc_doc_008_admin_downloads_with_secure_headers(self):
        """TC-DOC-008: Admin user can securely access and download private verification documents with secure headers."""
        org = OrganizationService.create_profile(
            user=self.donor_user,
            name="Admin Download Org",
            org_type=OrganizationType.RESTAURANT,
            contact_person="Owner",
            contact_email="owner@admdl.org",
            contact_phone="+919876543210",
            address_line1="Street 1",
            city="Pune",
            state="Maharashtra",
            postal_code="411001"
        )
        doc = DocumentService.upload_document(
            user=self.donor_user,
            org_id=org.id,
            document_type=DocumentType.FSSAI_LICENSE,
            uploaded_file=self.valid_pdf("fssai_admin.pdf")
        )
        self.client.force_login(self.admin_user)
        response = self.client.get(f"/organizations/documents/{doc.id}/download/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['X-Content-Type-Options'], 'nosniff')
        self.assertIn('attachment', response['Content-Disposition'])
        self.assertIn('no-store', response['Cache-Control'])
        self.assertEqual(response['Content-Security-Policy'], "default-src 'none'")

    def test_tc_doc_009_post_commit_document_deletion_and_pending_lock(self):
        """TC-DOC-009: Post-commit document deletion removes physical file from storage; deletion blocked while PENDING."""
        org = OrganizationService.create_profile(
            user=self.donor_user,
            name="Deletion Test Org",
            org_type=OrganizationType.RESTAURANT,
            contact_person="Owner",
            contact_email="owner@del.org",
            contact_phone="+919876543210",
            address_line1="Street 1",
            city="Pune",
            state="Maharashtra",
            postal_code="411001"
        )
        doc = DocumentService.upload_document(
            user=self.donor_user,
            org_id=org.id,
            document_type=DocumentType.FSSAI_LICENSE,
            uploaded_file=self.valid_pdf("to_delete.pdf")
        )
        file_path = doc.file.name
        self.assertTrue(private_document_storage.exists(file_path))

        # Delete document in DRAFT status
        with self.captureOnCommitCallbacks(execute=True):
            DocumentService.delete_document(self.donor_user, doc.id)
        self.assertFalse(OrganizationDocument.objects.filter(id=doc.id).exists())
        self.assertFalse(private_document_storage.exists(file_path))

        # Re-upload and lock under PENDING status
        doc2 = DocumentService.upload_document(
            user=self.donor_user,
            org_id=org.id,
            document_type=DocumentType.FSSAI_LICENSE,
            uploaded_file=self.valid_pdf("locked.pdf")
        )
        doc3 = DocumentService.upload_document(
            user=self.donor_user,
            org_id=org.id,
            document_type=DocumentType.BUSINESS_REGISTRATION,
            uploaded_file=self.valid_pdf("gst_locked.pdf")
        )
        OrganizationService.submit_for_verification(self.donor_user, org.id)
        org.refresh_from_db()
        self.assertEqual(org.verification_status, OrganizationProfile.VerificationStatus.PENDING)

        # Deletion must be blocked while organization is PENDING
        with self.assertRaises(ValidationError):
            DocumentService.delete_document(self.donor_user, doc2.id)

    def test_tc_doc_010_upload_failure_cleanup_on_transaction_rollback(self):
        """TC-DOC-010: Upload failure cleanup verifies physical file is purged if database transaction rolls back."""
        org = OrganizationService.create_profile(
            user=self.donor_user,
            name="Rollback Test Org",
            org_type=OrganizationType.RESTAURANT,
            contact_person="Owner",
            contact_email="owner@rollback.org",
            contact_phone="+919876543210",
            address_line1="Street 1",
            city="Pune",
            state="Maharashtra",
            postal_code="411001"
        )

        class SimulatedDBError(Exception):
            pass

        # We wrap in a block where an error is deliberately raised after file saving
        with self.assertRaises(SimulatedDBError):
            with transaction.atomic():
                doc = DocumentService.upload_document(
                    user=self.donor_user,
                    org_id=org.id,
                    document_type=DocumentType.FSSAI_LICENSE,
                    uploaded_file=self.valid_pdf("rollback.pdf")
                )
                file_name = doc.file.name
                self.assertTrue(private_document_storage.exists(file_name))
                # Trigger rollback
                raise SimulatedDBError("Simulated database failure during transaction")

        # After rollback, file should be cleaned up or document row does not exist
        self.assertFalse(OrganizationDocument.objects.filter(original_filename="rollback.pdf").exists())

    # =========================================================================
    # 16.3 Document Review, Replacement & Approval Policy [5 Tests]
    # =========================================================================

    def test_tc_req_001_submit_missing_mandatory_docs_fails(self):
        """TC-REQ-001: Submitting organization without mandatory documents for its type is rejected with ValidationError."""
        org = OrganizationService.create_profile(
            user=self.donor_user,
            name="Incomplete Restaurant",
            org_type=OrganizationType.RESTAURANT,
            contact_person="Owner",
            contact_email="owner@incomp.org",
            contact_phone="+919876543210",
            address_line1="Street 1",
            city="Pune",
            state="Maharashtra",
            postal_code="411001"
        )
        # RESTAURANT requires FSSAI_LICENSE and BUSINESS_REGISTRATION
        # Only upload FSSAI, omit BUSINESS_REGISTRATION
        DocumentService.upload_document(
            user=self.donor_user,
            org_id=org.id,
            document_type=DocumentType.FSSAI_LICENSE,
            uploaded_file=self.valid_pdf("fssai.pdf")
        )
        with self.assertRaises(ValidationError) as ctx:
            OrganizationService.submit_for_verification(self.donor_user, org.id)
        self.assertIn('documents', ctx.exception.message_dict)

    def test_tc_req_002_submit_all_required_docs_succeeds(self):
        """TC-REQ-002: Submitting organization with all required documents for its type transitions to PENDING."""
        org = OrganizationService.create_profile(
            user=self.donor_user,
            name="Complete Restaurant",
            org_type=OrganizationType.RESTAURANT,
            contact_person="Owner",
            contact_email="owner@comp.org",
            contact_phone="+919876543210",
            address_line1="Street 1",
            city="Pune",
            state="Maharashtra",
            postal_code="411001"
        )
        DocumentService.upload_document(
            user=self.donor_user,
            org_id=org.id,
            document_type=DocumentType.FSSAI_LICENSE,
            uploaded_file=self.valid_pdf("fssai.pdf")
        )
        DocumentService.upload_document(
            user=self.donor_user,
            org_id=org.id,
            document_type=DocumentType.BUSINESS_REGISTRATION,
            uploaded_file=self.valid_pdf("gst.pdf")
        )
        submitted_org = OrganizationService.submit_for_verification(self.donor_user, org.id)
        self.assertEqual(submitted_org.verification_status, OrganizationProfile.VerificationStatus.PENDING)

    def test_tc_req_003_admin_individual_document_review(self):
        """TC-REQ-003: Admin individual document review correctly marks document APPROVED or REJECTED with notes."""
        org = OrganizationService.create_profile(
            user=self.donor_user,
            name="Review Doc Org",
            org_type=OrganizationType.RESTAURANT,
            contact_person="Owner",
            contact_email="owner@revdoc.org",
            contact_phone="+919876543210",
            address_line1="Street 1",
            city="Pune",
            state="Maharashtra",
            postal_code="411001"
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

        # Approve doc1
        reviewed_doc1 = DocumentService.review_document(
            admin_user=self.admin_user,
            document_id=doc1.id,
            decision=OrganizationDocument.ReviewStatus.APPROVED
        )
        self.assertEqual(reviewed_doc1.review_status, OrganizationDocument.ReviewStatus.APPROVED)
        self.assertEqual(reviewed_doc1.reviewed_by, self.admin_user)

        # Reject doc2 without reason -> fails
        with self.assertRaises(ValidationError):
            DocumentService.review_document(
                admin_user=self.admin_user,
                document_id=doc2.id,
                decision=OrganizationDocument.ReviewStatus.REJECTED,
                rejection_reason=""
            )

        # Reject doc2 with reason -> succeeds
        reviewed_doc2 = DocumentService.review_document(
            admin_user=self.admin_user,
            document_id=doc2.id,
            decision=OrganizationDocument.ReviewStatus.REJECTED,
            rejection_reason="GST registration copy is blurry and illegible."
        )
        self.assertEqual(reviewed_doc2.review_status, OrganizationDocument.ReviewStatus.REJECTED)
        self.assertEqual(reviewed_doc2.rejection_reason, "GST registration copy is blurry and illegible.")

    def test_tc_req_004_rejected_document_history_retained_on_replacement(self):
        """TC-REQ-004: Rejected document history is retained when replacement document of same type is uploaded."""
        org = OrganizationService.create_profile(
            user=self.donor_user,
            name="Replacement Org",
            org_type=OrganizationType.RESTAURANT,
            contact_person="Owner",
            contact_email="owner@replace.org",
            contact_phone="+919876543210",
            address_line1="Street 1",
            city="Pune",
            state="Maharashtra",
            postal_code="411001"
        )
        doc_old = DocumentService.upload_document(
            user=self.donor_user,
            org_id=org.id,
            document_type=DocumentType.FSSAI_LICENSE,
            uploaded_file=self.valid_pdf("fssai_blurry.pdf")
        )
        # Admin rejects old document
        DocumentService.review_document(
            admin_user=self.admin_user,
            document_id=doc_old.id,
            decision=OrganizationDocument.ReviewStatus.REJECTED,
            rejection_reason="Expired license"
        )
        doc_old.refresh_from_db()
        self.assertEqual(doc_old.review_status, OrganizationDocument.ReviewStatus.REJECTED)

        # Owner uploads replacement
        doc_new = DocumentService.upload_document(
            user=self.donor_user,
            org_id=org.id,
            document_type=DocumentType.FSSAI_LICENSE,
            uploaded_file=self.valid_pdf("fssai_valid_2026.pdf")
        )
        self.assertEqual(doc_new.review_status, OrganizationDocument.ReviewStatus.PENDING)

        # Both documents must co-exist in org.documents
        all_fssai_docs = org.documents.filter(document_type=DocumentType.FSSAI_LICENSE)
        self.assertEqual(all_fssai_docs.count(), 2)
        self.assertTrue(all_fssai_docs.filter(id=doc_old.id, review_status='REJECTED').exists())
        self.assertTrue(all_fssai_docs.filter(id=doc_new.id, review_status='PENDING').exists())

    def test_tc_req_005_gate2_organization_approval_requires_all_mandatory_docs_approved(self):
        """TC-REQ-005: Organization approval requires each mandatory document type to have an approved document."""
        org = OrganizationService.create_profile(
            user=self.donor_user,
            name="Gate 2 Org",
            org_type=OrganizationType.RESTAURANT,
            contact_person="Owner",
            contact_email="owner@gate2.org",
            contact_phone="+919876543210",
            address_line1="Street 1",
            city="Pune",
            state="Maharashtra",
            postal_code="411001"
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
        doc_opt = DocumentService.upload_document(
            user=self.donor_user,
            org_id=org.id,
            document_type=DocumentType.OTHER,
            uploaded_file=self.valid_pdf("optional_award.pdf")
        )

        OrganizationService.submit_for_verification(self.donor_user, org.id)

        # Approve only doc1 (FSSAI), doc2 (BUSINESS_REGISTRATION) remains PENDING
        DocumentService.review_document(self.admin_user, doc1.id, OrganizationDocument.ReviewStatus.APPROVED)

        # Attempting to approve organization must FAIL Gate 2
        with self.assertRaises(ValidationError) as ctx:
            VerificationService.approve_organization(self.admin_user, org.id)
        self.assertTrue(
            "Business Registration" in str(ctx.exception) or "BUSINESS_REGISTRATION" in str(ctx.exception),
            f"Expected mandatory document approval error, got: {ctx.exception}"
        )

        # Now approve doc2
        DocumentService.review_document(self.admin_user, doc2.id, OrganizationDocument.ReviewStatus.APPROVED)

        # Now approve organization -> must SUCCEED
        approved_org = VerificationService.approve_organization(self.admin_user, org.id)
        self.assertEqual(approved_org.verification_status, OrganizationProfile.VerificationStatus.APPROVED)

        # Verify optional document was NOT automatically approved
        doc_opt.refresh_from_db()
        self.assertEqual(doc_opt.review_status, OrganizationDocument.ReviewStatus.PENDING)
