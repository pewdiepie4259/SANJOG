import uuid
from decimal import Decimal
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.contrib import admin
from django.core.exceptions import PermissionDenied

from apps.accounts.models import CustomUser
from apps.accounts.forms import CustomUserCreationForm, CustomUserChangeForm
from apps.accounts.services import AuthService
from apps.organizations.models import (
    OrganizationProfile,
    OrganizationDocument,
    OrganizationVerificationEvent,
)
from apps.organizations.validators import OrganizationType, DocumentType
from apps.organizations.services import OrganizationService, DocumentService

User = get_user_model()


class DjangoAdminPanelTestCase(TestCase):
    """
    Comprehensive test suite for SANJOG Django Administration:
    - URL routing, authentication, and authorization boundaries
    - CustomUser administration, role guards, and privilege escalation defense
    - Organization profile administration, inlines, Gate 2 enforcement, and actions
    - Private document storage rendering and secure streaming authorization
    - Verification audit event immutability
    - Branding verification
    """

    def setUp(self):
        self.client = Client()

        # 1. Active Superuser
        self.superuser = User.objects.create_superuser(
            username='admin_test_root',
            email='admin_root@sanjog.org',
            password='RootPassword123!',
            role=User.RoleChoices.ADMIN,
        )

        # 2. Non-staff Donor User
        self.donor_user = AuthService.register_user(
            username='donor_test_client',
            email='donor_client@sanjog.org',
            password='DonorPassword123!',
            role=User.RoleChoices.DONOR,
        )

        # 3. Staff User with limited permissions (change_customuser only)
        self.staff_user = User.objects.create_user(
            username='staff_limited',
            email='staff_limited@sanjog.org',
            password='StaffPassword123!',
            is_staff=True,
            is_superuser=False,
            role=User.RoleChoices.DONOR,
        )
        user_ct = ContentType.objects.get_for_model(CustomUser)
        change_user_perm = Permission.objects.get(content_type=user_ct, codename='change_customuser')
        view_user_perm = Permission.objects.get(content_type=user_ct, codename='view_customuser')
        self.staff_user.user_permissions.add(change_user_perm, view_user_perm)

        # 4. Inactive Account
        self.inactive_user = User.objects.create_user(
            username='inactive_account',
            email='inactive@sanjog.org',
            password='InactivePassword123!',
            is_active=False,
            is_staff=True,
            is_superuser=False,
        )

        # Helper valid file buffer for private document testing
        self.valid_pdf = SimpleUploadedFile(
            "fssai_cert.pdf",
            b"%PDF-1.4\n1 0 obj<<>>endobj\ntrailer<<>>startxref\n%%EOF\n",
            content_type="application/pdf"
        )

    # =========================================================================
    # 1. URL Routing & Authentication Boundaries
    # =========================================================================

    def test_tc_adm_001_admin_url_resolution_anonymous(self):
        """TC-ADM-001: Anonymous request to /admin/ redirects to /admin/login/?next=/admin/."""
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/login/', response.url)

    def test_tc_adm_002_superuser_authentication_success(self):
        """TC-ADM-002: Authorized superuser authenticates and accesses admin dashboard."""
        self.client.force_login(self.superuser)
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "SANJOG Food Rescue OS — Administration")

    def test_tc_adm_003_non_staff_user_blocked(self):
        """TC-ADM-003: Authenticated non-staff user is blocked from admin index."""
        self.client.force_login(self.donor_user)
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/login/', response.url)

    def test_tc_adm_004_inactive_account_blocked(self):
        """TC-ADM-004: Inactive account cannot authenticate into admin."""
        logged_in = self.client.login(username='inactive_account', password='InactivePassword123!')
        self.assertFalse(logged_in)
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 302)

    # =========================================================================
    # 2. CustomUser Administration & Privilege / Role Defense
    # =========================================================================

    def test_tc_adm_005_custom_user_creation_via_form(self):
        """TC-ADM-005: CustomUser creation form properly hashes password and sets fields."""
        form_data = {
            'username': 'new_created_user',
            'email': 'new_created@sanjog.org',
            'role': User.RoleChoices.RECEIVER,
            'phone_number': '+919876543299',
            'first_name': 'New',
            'last_name': 'Receiver',
            'usable_password': 'true',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!',
        }
        form = CustomUserCreationForm(data=form_data, current_user=self.superuser)
        self.assertTrue(form.is_valid(), form.errors)
        created_user = form.save()
        self.assertEqual(created_user.username, 'new_created_user')
        self.assertEqual(created_user.role, User.RoleChoices.RECEIVER)
        self.assertTrue(created_user.has_usable_password())
        self.assertTrue(created_user.check_password('SecurePass123!'))
        self.assertIsInstance(created_user.id, uuid.UUID)


    def test_tc_adm_006_privilege_escalation_guard_ui(self):
        """TC-ADM-006: Non-superuser staff sees privilege flags as read-only and fieldsets restricted."""
        model_admin = admin.site._registry[CustomUser]
        
        class FakeStaffRequest:
            user = self.staff_user

        req = FakeStaffRequest()
        readonly = model_admin.get_readonly_fields(req, self.donor_user)
        for priv_field in ['is_superuser', 'is_staff', 'groups', 'user_permissions']:
            self.assertIn(priv_field, readonly)

        fieldsets = model_admin.get_fieldsets(req, self.donor_user)
        fieldset_names = [fs[0] for fs in fieldsets]
        self.assertNotIn('Permissions', fieldset_names)

    def test_tc_adm_007_privilege_escalation_crafted_post_flags(self):
        """TC-ADM-007: Non-superuser staff cannot escalate privileges via crafted POST flags."""
        self.client.force_login(self.staff_user)
        change_url = reverse('admin:accounts_customuser_change', args=[self.donor_user.pk])
        
        post_data = {
            'username': self.donor_user.username,
            'email': self.donor_user.email,
            'role': User.RoleChoices.DONOR,
            'is_superuser': 'on',  # Crafted attempt
            'is_staff': 'on',      # Crafted attempt
            'is_active': 'on',
        }
        response = self.client.post(change_url, post_data)
        self.donor_user.refresh_from_db()
        self.assertFalse(self.donor_user.is_superuser)
        self.assertFalse(self.donor_user.is_staff)

    def test_tc_adm_008_privilege_escalation_crafted_post_m2m(self):
        """TC-ADM-008: Non-superuser staff cannot inject groups or user_permissions via crafted POST."""
        test_group = Group.objects.create(name='PrivilegedGroup')
        self.client.force_login(self.staff_user)
        change_url = reverse('admin:accounts_customuser_change', args=[self.donor_user.pk])
        
        post_data = {
            'username': self.donor_user.username,
            'email': self.donor_user.email,
            'role': User.RoleChoices.DONOR,
            'groups': [test_group.id],  # Crafted attempt
            'is_active': 'on',
        }
        self.client.post(change_url, post_data)
        self.donor_user.refresh_from_db()
        self.assertNotIn(test_group, self.donor_user.groups.all())

    def test_tc_adm_009a_role_escalation_self_promotion_blocked(self):
        """TC-ADM-009A: Non-superuser staff cannot promote themselves to role='ADMIN'."""
        self.client.force_login(self.staff_user)
        change_url = reverse('admin:accounts_customuser_change', args=[self.staff_user.pk])
        
        post_data = {
            'username': self.staff_user.username,
            'email': self.staff_user.email,
            'role': User.RoleChoices.ADMIN,  # Crafted self-escalation attempt
            'is_active': 'on',
        }
        response = self.client.post(change_url, post_data)
        self.staff_user.refresh_from_db()
        self.assertNotEqual(self.staff_user.role, User.RoleChoices.ADMIN)
        self.assertEqual(self.staff_user.role, User.RoleChoices.DONOR)

    def test_tc_adm_009b_role_escalation_cross_promotion_blocked(self):
        """TC-ADM-009B: Non-superuser staff cannot promote another user to role='ADMIN'."""
        self.client.force_login(self.staff_user)
        change_url = reverse('admin:accounts_customuser_change', args=[self.donor_user.pk])
        
        post_data = {
            'username': self.donor_user.username,
            'email': self.donor_user.email,
            'role': User.RoleChoices.ADMIN,  # Crafted cross-escalation attempt
            'is_active': 'on',
        }
        response = self.client.post(change_url, post_data)
        self.donor_user.refresh_from_db()
        self.assertNotEqual(self.donor_user.role, User.RoleChoices.ADMIN)
        self.assertFalse(self.donor_user.is_admin_user)

    def test_tc_adm_009c_admin_role_account_protection(self):
        """TC-ADM-009C: Non-superuser staff cannot edit or delete any user holding role='ADMIN'."""
        admin_account = User.objects.create_user(
            username='admin_persona',
            email='admin_persona@sanjog.org',
            password='AdminPassword123!',
            role=User.RoleChoices.ADMIN,
        )
        model_admin = admin.site._registry[CustomUser]
        
        class FakeStaffRequest:
            user = self.staff_user

        req = FakeStaffRequest()
        self.assertFalse(model_admin.has_change_permission(req, admin_account))
        self.assertFalse(model_admin.has_delete_permission(req, admin_account))

    def test_tc_adm_009d_superuser_role_assignment_succeeds(self):
        """TC-ADM-009D: Superuser can legitimately assign role='ADMIN'."""
        self.client.force_login(self.superuser)
        change_url = reverse('admin:accounts_customuser_change', args=[self.donor_user.pk])
        
        post_data = {
            'username': self.donor_user.username,
            'email': self.donor_user.email,
            'role': User.RoleChoices.ADMIN,
            'is_active': 'on',
        }
        response = self.client.post(change_url, post_data)
        self.donor_user.refresh_from_db()
        self.assertEqual(self.donor_user.role, User.RoleChoices.ADMIN)
        self.assertTrue(self.donor_user.is_admin_user)

    def test_tc_adm_010_superuser_record_edit_protection(self):
        """TC-ADM-010: Non-superuser staff cannot edit superuser accounts."""
        model_admin = admin.site._registry[CustomUser]
        
        class FakeStaffRequest:
            user = self.staff_user

        req = FakeStaffRequest()
        self.assertFalse(model_admin.has_change_permission(req, self.superuser))

    def test_tc_adm_011_superuser_record_delete_protection(self):
        """TC-ADM-011: Non-superuser staff cannot delete superuser accounts."""
        model_admin = admin.site._registry[CustomUser]
        
        class FakeStaffRequest:
            user = self.staff_user

        req = FakeStaffRequest()
        self.assertFalse(model_admin.has_delete_permission(req, self.superuser))

    def test_tc_adm_012_normal_superuser_admin_works(self):
        """TC-ADM-012: Active superuser can freely manage staff status and permissions."""
        self.client.force_login(self.superuser)
        change_url = reverse('admin:accounts_customuser_change', args=[self.donor_user.pk])
        
        post_data = {
            'username': self.donor_user.username,
            'email': self.donor_user.email,
            'role': User.RoleChoices.DONOR,
            'is_staff': 'on',
            'is_active': 'on',
        }
        self.client.post(change_url, post_data)
        self.donor_user.refresh_from_db()
        self.assertTrue(self.donor_user.is_staff)

    # =========================================================================
    # 3. Organization Administration, Private Storage & Actions
    # =========================================================================

    def _create_sample_org_and_doc(self):
        """Helper to create an organization profile and upload a private compliance document."""
        org = OrganizationService.create_profile(
            user=self.donor_user,
            name="Harvest Kitchens",
            org_type=OrganizationType.RESTAURANT,
            registration_number="REG-HK-8899",
            contact_person="Ramesh Gupta",
            contact_email="ramesh@harvestkitchens.org",
            contact_phone="+919876543201",
            address_line1="14 Industrial Lane",
            city="Bengaluru",
            state="Karnataka",
            postal_code="560001",
        )
        doc = DocumentService.upload_document(
            user=self.donor_user,
            org_id=org.id,
            document_type=DocumentType.FSSAI_LICENSE,
            uploaded_file=self.valid_pdf,
        )
        return org, doc

    def test_tc_adm_013_private_storage_admin_rendering(self):
        """TC-ADM-013: Admin change pages render without throwing ValueError on private storage file.url."""
        org, doc = self._create_sample_org_and_doc()
        self.client.force_login(self.superuser)

        # 1. Document change page
        doc_change_url = reverse('admin:organizations_organizationdocument_change', args=[doc.pk])
        response = self.client.get(doc_change_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Download File")

        # 2. Organization change page with inlines
        org_change_url = reverse('admin:organizations_organizationprofile_change', args=[org.pk])
        response = self.client.get(org_change_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Download File")

    def test_tc_adm_014_document_download_endpoint_authorized(self):
        """TC-ADM-014: Authorized admin streams private document with strict security headers."""
        org, doc = self._create_sample_org_and_doc()
        self.client.force_login(self.superuser)

        download_url = reverse('organization_document_download', kwargs={'doc_id': doc.id})
        response = self.client.get(download_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['X-Content-Type-Options'], 'nosniff')
        self.assertEqual(response['Content-Security-Policy'], "default-src 'none'")
        self.assertIn('attachment', response['Content-Disposition'])
        self.assertIn(doc.original_filename, response['Content-Disposition'])

    def test_tc_adm_015_document_download_endpoint_denied(self):
        """TC-ADM-015: Unauthorized non-owner receives HTTP 403 on private document download."""
        org, doc = self._create_sample_org_and_doc()
        unauthorized_donor = AuthService.register_user(
            username='stranger_donor',
            email='stranger@sanjog.org',
            password='StrangerPassword123!',
            role=User.RoleChoices.DONOR,
        )
        self.client.force_login(unauthorized_donor)

        download_url = reverse('organization_document_download', kwargs={'doc_id': doc.id})
        response = self.client.get(download_url)
        self.assertEqual(response.status_code, 403)

    def test_tc_adm_016_document_review_action_approve(self):
        """TC-ADM-016: Admin executes document approve action successfully."""
        org, doc = self._create_sample_org_and_doc()
        self.client.force_login(self.superuser)

        changelist_url = reverse('admin:organizations_organizationdocument_changelist')
        post_data = {
            'action': 'approve_document_action',
            '_selected_action': [doc.pk],
        }
        response = self.client.post(changelist_url, post_data, follow=True)
        self.assertEqual(response.status_code, 200)
        doc.refresh_from_db()
        self.assertEqual(doc.review_status, OrganizationDocument.ReviewStatus.APPROVED)
        self.assertEqual(doc.reviewed_by, self.superuser)

    def test_tc_adm_017a_document_review_action_permission_denied(self):
        """TC-ADM-017A: Staff lacking change_organizationdocument permission cannot approve documents."""
        org, doc = self._create_sample_org_and_doc()
        self.client.force_login(self.staff_user)

        changelist_url = reverse('admin:organizations_organizationdocument_changelist')
        post_data = {
            'action': 'approve_document_action',
            '_selected_action': [doc.pk],
        }
        response = self.client.post(changelist_url, post_data)
        self.assertEqual(response.status_code, 403)
        doc.refresh_from_db()
        self.assertEqual(doc.review_status, OrganizationDocument.ReviewStatus.PENDING)

    def test_tc_adm_017b_document_rejection_requires_reason(self):
        """TC-ADM-017B: Document rejection requires a non-empty rejection reason."""
        org, doc = self._create_sample_org_and_doc()
        self.client.force_login(self.superuser)

        changelist_url = reverse('admin:organizations_organizationdocument_changelist')
        
        # 1. First trigger renders intermediate confirmation form
        post_data = {
            'action': 'reject_document_action',
            '_selected_action': [doc.pk],
        }
        response = self.client.post(changelist_url, post_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Mandatory Document Rejection Reason")

        # 2. Submitting empty rejection reason fails
        confirm_data = {
            'action': 'reject_document_action',
            '_selected_action': [doc.pk],
            'post': 'yes',
            'rejection_reason': '   ',
        }
        response = self.client.post(changelist_url, confirm_data, follow=True)
        doc.refresh_from_db()
        self.assertEqual(doc.review_status, OrganizationDocument.ReviewStatus.PENDING)

        # 3. Submitting valid rejection reason succeeds
        confirm_data['rejection_reason'] = 'Document is blurred and unreadable.'
        response = self.client.post(changelist_url, confirm_data, follow=True)
        doc.refresh_from_db()
        self.assertEqual(doc.review_status, OrganizationDocument.ReviewStatus.REJECTED)
        self.assertEqual(doc.rejection_reason, 'Document is blurred and unreadable.')

    def test_tc_adm_018a_organization_approval_gate_2_enforced(self):
        """TC-ADM-018A: Organization approval fails Gate 2 if mandatory documents are missing/unapproved."""
        org, doc = self._create_sample_org_and_doc()
        # Submit for verification -> PENDING
        # Note: RESTAURANT requires FSSAI_LICENSE and BUSINESS_REGISTRATION
        # We only uploaded FSSAI_LICENSE, so Gate 1 is incomplete unless both uploaded.
        doc2 = DocumentService.upload_document(
            user=self.donor_user,
            org_id=org.id,
            document_type=DocumentType.BUSINESS_REGISTRATION,
            uploaded_file=SimpleUploadedFile("br.pdf", b"%PDF-1.4\n1 0 obj<<>>endobj\ntrailer<<>>startxref\n%%EOF\n", "application/pdf")
        )
        OrganizationService.submit_for_verification(self.donor_user, org.id)
        org.refresh_from_db()
        self.assertEqual(org.verification_status, OrganizationProfile.VerificationStatus.PENDING)

        self.client.force_login(self.superuser)
        changelist_url = reverse('admin:organizations_organizationprofile_changelist')
        post_data = {
            'action': 'approve_organization_action',
            '_selected_action': [org.pk],
        }
        response = self.client.post(changelist_url, post_data, follow=True)
        self.assertEqual(response.status_code, 200)
        org.refresh_from_db()
        # Must fail Gate 2 because neither FSSAI nor Business Reg has been APPROVED
        self.assertEqual(org.verification_status, OrganizationProfile.VerificationStatus.PENDING)
        self.assertContains(response, "Mandatory document(s) have not been individually approved")

    def test_tc_adm_018b_organization_approval_permission_denied(self):
        """TC-ADM-018B: Staff lacking change_organizationprofile permission cannot approve organizations."""
        org, doc = self._create_sample_org_and_doc()
        self.client.force_login(self.staff_user)

        changelist_url = reverse('admin:organizations_organizationprofile_changelist')
        post_data = {
            'action': 'approve_organization_action',
            '_selected_action': [org.pk],
        }
        response = self.client.post(changelist_url, post_data)
        self.assertEqual(response.status_code, 403)

    def test_tc_adm_019_organization_approval_success(self):
        """TC-ADM-019: Organization is approved when all mandatory documents are APPROVED."""
        org, doc = self._create_sample_org_and_doc()
        doc2 = DocumentService.upload_document(
            user=self.donor_user,
            org_id=org.id,
            document_type=DocumentType.BUSINESS_REGISTRATION,
            uploaded_file=SimpleUploadedFile("br.pdf", b"%PDF-1.4\n1 0 obj<<>>endobj\ntrailer<<>>startxref\n%%EOF\n", "application/pdf")
        )
        OrganizationService.submit_for_verification(self.donor_user, org.id)
        
        # Approve both mandatory documents
        DocumentService.review_document(self.superuser, doc.id, OrganizationDocument.ReviewStatus.APPROVED)
        DocumentService.review_document(self.superuser, doc2.id, OrganizationDocument.ReviewStatus.APPROVED)

        self.client.force_login(self.superuser)
        changelist_url = reverse('admin:organizations_organizationprofile_changelist')
        post_data = {
            'action': 'approve_organization_action',
            '_selected_action': [org.pk],
        }
        response = self.client.post(changelist_url, post_data, follow=True)
        self.assertEqual(response.status_code, 200)
        org.refresh_from_db()
        self.assertEqual(org.verification_status, OrganizationProfile.VerificationStatus.APPROVED)
        self.assertEqual(org.verified_by, self.superuser)

        # Verify audit event created
        event = org.verification_events.latest('created_at')
        self.assertEqual(event.event_type, OrganizationVerificationEvent.EventType.APPROVED)
        self.assertEqual(event.actor, self.superuser)

    def test_tc_adm_020_organization_rejection_requires_reason(self):
        """TC-ADM-020: Organization rejection requires a mandatory reason and records audit event."""
        org, doc = self._create_sample_org_and_doc()
        doc2 = DocumentService.upload_document(
            user=self.donor_user,
            org_id=org.id,
            document_type=DocumentType.BUSINESS_REGISTRATION,
            uploaded_file=SimpleUploadedFile("br.pdf", b"%PDF-1.4\n1 0 obj<<>>endobj\ntrailer<<>>startxref\n%%EOF\n", "application/pdf")
        )
        OrganizationService.submit_for_verification(self.donor_user, org.id)

        self.client.force_login(self.superuser)
        changelist_url = reverse('admin:organizations_organizationprofile_changelist')

        # 1. Confirmation form rendered
        post_data = {
            'action': 'reject_organization_action',
            '_selected_action': [org.pk],
        }
        response = self.client.post(changelist_url, post_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Mandatory Rejection Reason")

        # 2. Confirm rejection with reason
        confirm_data = {
            'action': 'reject_organization_action',
            '_selected_action': [org.pk],
            'post': 'yes',
            'rejection_reason': 'FSSAI License registration number does not match regulatory registry.',
        }
        response = self.client.post(changelist_url, confirm_data, follow=True)
        org.refresh_from_db()
        self.assertEqual(org.verification_status, OrganizationProfile.VerificationStatus.REJECTED)
        self.assertEqual(org.rejection_reason, 'FSSAI License registration number does not match regulatory registry.')

        # Audit event created
        event = org.verification_events.latest('created_at')
        self.assertEqual(event.event_type, OrganizationVerificationEvent.EventType.REJECTED)
        self.assertEqual(event.notes, 'FSSAI License registration number does not match regulatory registry.')

    # =========================================================================
    # 4. Audit Event Immutability & Admin Branding
    # =========================================================================

    def test_tc_adm_021_standalone_audit_event_immutability(self):
        """TC-ADM-021: OrganizationVerificationEventAdmin disables add, change, and delete permissions."""
        model_admin = admin.site._registry[OrganizationVerificationEvent]
        
        class FakeRequest:
            user = self.superuser

        req = FakeRequest()
        self.assertFalse(model_admin.has_add_permission(req))
        self.assertFalse(model_admin.has_change_permission(req))
        self.assertFalse(model_admin.has_delete_permission(req))
        self.assertIsNone(model_admin.actions)

    def test_tc_adm_022_inline_audit_event_immutability(self):
        """TC-ADM-022: OrganizationVerificationEventInline disables add, change, and delete permissions."""
        from apps.organizations.admin import OrganizationVerificationEventInline
        inline = OrganizationVerificationEventInline(OrganizationProfile, admin.site)
        
        class FakeRequest:
            user = self.superuser

        req = FakeRequest()
        self.assertFalse(inline.has_add_permission(req, None))
        self.assertFalse(inline.has_change_permission(req, None))
        self.assertFalse(inline.has_delete_permission(req, None))
        self.assertFalse(inline.can_delete)

    def test_tc_adm_023_admin_branding_configured(self):
        """TC-ADM-023: Admin portal branding titles and headers are customized."""
        self.assertEqual(admin.site.site_header, "SANJOG Food Rescue OS — Administration")
        self.assertEqual(admin.site.site_title, "SANJOG Admin")
        self.assertEqual(admin.site.index_title, "Operational Governance & Verification Portal")
